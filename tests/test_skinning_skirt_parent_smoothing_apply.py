from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import skirt_parent_smoothing_apply as module


class SkirtParentSmoothingApplyTests(unittest.TestCase):
    def test_applies_gradient_then_propagates_ratios(self):
        calls = []
        plan = {'operations': [{'influences': ['jA', 'jB'], 'active_joint': 'jB', 'root_vertices': ['m.vtx[1]', 'm.vtx[2]'], 'strips': {'m.vtx[1]': ['m.vtx[1]', 'm.vtx[5]'], 'm.vtx[2]': ['m.vtx[6]']}}]}
        def gradient(*args, **kwargs):
            calls.append(('gradient', args[1], args[2], args[3], args[4]))
            return list(args[1])
        def copy(*args, **kwargs):
            calls.append(('copy', args[1], args[2], args[3]))
            return list(args[2])
        result = module.apply_smoothing_plan('skin', plan, distance_provider=lambda vertex, joint: {'m.vtx[1]': 1.0, 'm.vtx[2]': 2.0}[vertex], gradient_applier=gradient, ratio_copier=copy)
        self.assertEqual(calls[0], ('gradient', ['m.vtx[1]', 'm.vtx[2]'], 'jB', ['jA', 'jB'], [1.0, 2.0]))
        self.assertEqual(calls[1], ('copy', 'm.vtx[1]', ['m.vtx[5]'], ['jA', 'jB']))
        self.assertEqual(calls[2], ('copy', 'm.vtx[2]', ['m.vtx[6]'], ['jA', 'jB']))
        self.assertEqual(result[0]['gradient_vertices'], ['m.vtx[1]', 'm.vtx[2]'])

    def test_empty_root_vertices_are_noop(self):
        result = module.apply_smoothing_plan('skin', {'operations': [{'influences': ['jA', 'jB'], 'active_joint': 'jB', 'root_vertices': [], 'strips': {}}]})
        self.assertEqual(result, [{'active_joint': 'jB', 'gradient_vertices': [], 'propagated': {}}])

    def test_invalid_operation_fails(self):
        with self.assertRaises(ValueError):
            module.apply_smoothing_plan('skin', {'operations': [{'influences': ['jA'], 'active_joint': 'jB'}]})

    def test_requires_skin_cluster_and_plan(self):
        with self.assertRaises(ValueError):
            module.apply_smoothing_plan('', {'operations': []})
        with self.assertRaises(ValueError):
            module.apply_smoothing_plan('skin', None)


if __name__ == '__main__':
    unittest.main()
