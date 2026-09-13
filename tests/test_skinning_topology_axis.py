from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning.topology_axis import choose_edge_by_axis


class TopologyAxisTests(unittest.TestCase):
    def test_parallel_edge(self):
        self.assertEqual(choose_edge_by_axis([(2, (0, 1, 0)), (5, (2, 0, 0))], (1, 0, 0)), 5)

    def test_perpendicular_edge(self):
        self.assertEqual(choose_edge_by_axis([(2, (0, 1, 0)), (5, (2, 0, 0))], (1, 0, 0), perpendicular=True), 2)

    def test_normalizes_vectors(self):
        self.assertEqual(choose_edge_by_axis([(1, (10, 0, 0)), (2, (1, 1, 0))], (3, 0, 0)), 1)

    def test_rejects_zero_axis(self):
        with self.assertRaises(ValueError):
            choose_edge_by_axis([(1, (1, 0, 0))], (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
