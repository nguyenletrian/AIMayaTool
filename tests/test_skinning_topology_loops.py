from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import topology_loops


class TopologyLoopsTests(unittest.TestCase):
    def test_edge_loop_expands_numeric_edge(self):
        calls = []
        def selector(mesh, **kwargs):
            calls.append((mesh, kwargs))
            return [3, 7, 11]
        self.assertEqual(topology_loops.edge_loop('meshShape', 7, selector=selector), ['meshShape.e[3]', 'meshShape.e[7]', 'meshShape.e[11]'])
        self.assertEqual(calls[0][1], {'edgeLoop': 7, 'noSelection': True})

    def test_edge_loop_empty_when_selector_has_no_path(self):
        self.assertEqual(topology_loops.edge_loop('meshShape', 'meshShape.e[2]', selector=lambda *args, **kwargs: None), [])

    def test_joint_axis_edge_loop_composes_edge_choice_and_loop(self):
        calls = []
        def choose(mesh, joint, vertex_index, perpendicular=False):
            calls.append((mesh, joint, vertex_index, perpendicular))
            return 5
        result = topology_loops.joint_axis_edge_loop('meshShape', 'joint1', 4, edge_selector=choose, loop_selector=lambda *args, **kwargs: [5, 9])
        self.assertEqual(result, ['meshShape.e[5]', 'meshShape.e[9]'])
        self.assertEqual(calls, [('meshShape', 'joint1', 4, False)])

    def test_joint_axis_edge_loop_preserves_perpendicular_mode_and_none(self):
        seen = []
        def choose(mesh, joint, vertex_index, perpendicular=False):
            seen.append(perpendicular)
            return None
        self.assertEqual(topology_loops.joint_axis_edge_loop('meshShape', 'joint1', 1, perpendicular=True, edge_selector=choose), [])
        self.assertEqual(seen, [True])


if __name__ == '__main__':
    unittest.main()
