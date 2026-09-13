from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import skirt_parent_smoothing


class SkirtParentSmoothingTests(unittest.TestCase):
    def test_builds_operations_from_spans(self):
        calls = []
        def groups(mesh, vertices, mesh_fn=None, selector=None):
            calls.append((mesh, list(vertices)))
            return {vertices[0]: ['mesh.vtx[10]', 'mesh.vtx[11]']}
        plan = {'mesh': 'mesh', 'joint_parent': 'parent', 'closed': True, 'spans': [
            {'source_joint': 'jA', 'target_joint': 'jB', 'vertices': ['mesh.vtx[1]', 'mesh.vtx[2]']},
            {'source_joint': 'jB', 'target_joint': 'jA', 'vertices': ['mesh.vtx[3]']},
        ]}
        result = skirt_parent_smoothing.build_smoothing_plan(plan, group_builder=groups)
        self.assertTrue(result['closed'])
        self.assertEqual(len(result['operations']), 2)
        self.assertEqual(result['operations'][0]['active_joint'], 'jB')
        self.assertEqual(result['operations'][0]['influences'], ['jA', 'jB'])
        self.assertEqual(calls[0], ('mesh', ['mesh.vtx[1]', 'mesh.vtx[2]']))

    def test_empty_vertices_produce_empty_strips(self):
        plan = {'mesh': 'mesh', 'spans': [{'source_joint': 'jA', 'target_joint': 'jB', 'vertices': []}]}
        result = skirt_parent_smoothing.build_smoothing_plan(plan, group_builder=lambda *args, **kwargs: self.fail('should not be called'))
        self.assertEqual(result['operations'][0]['strips'], {})

    def test_requires_plan_mesh(self):
        with self.assertRaises(ValueError):
            skirt_parent_smoothing.build_smoothing_plan({'spans': []})

    def test_requires_span_joints(self):
        with self.assertRaises(ValueError):
            skirt_parent_smoothing.build_smoothing_plan({'mesh': 'mesh', 'spans': [{'vertices': ['mesh.vtx[1]']}]})


if __name__ == '__main__':
    unittest.main()
