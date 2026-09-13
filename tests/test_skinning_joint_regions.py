from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import joint_regions


class JointRegionsTests(unittest.TestCase):
    def test_circular_order_returns_all_items(self):
        positions = {'a': (1, 0, 0), 'b': (0, 1, 0), 'c': (-1, 0, 0), 'd': (0, -1, 0)}
        result = joint_regions.circular_order(['a', 'b', 'c', 'd'], positions)
        self.assertEqual(set(result), {'a', 'b', 'c', 'd'})
        self.assertEqual(len(result), 4)

    def test_circular_order_clockwise_reverses_direction(self):
        positions = {'a': (1, 0, 0), 'b': (0, 1, 0), 'c': (-1, 0, 0), 'd': (0, -1, 0)}
        ccw = joint_regions.circular_order(['a', 'b', 'c', 'd'], positions)
        cw = joint_regions.circular_order(['a', 'b', 'c', 'd'], positions, clockwise=True)
        self.assertEqual(cw, list(reversed(ccw)))

    def test_closest_items_excludes_target_and_sorts(self):
        positions = {'a': (0, 0, 0), 'b': (1, 0, 0), 'c': (3, 0, 0)}
        self.assertEqual(joint_regions.closest_items('a', positions, 2), [('b', 1.0), ('c', 3.0)])

    def test_indices_within_radius_is_inclusive(self):
        points = [(0, 0, 0), (1, 0, 0), (2, 0, 0)]
        self.assertEqual(joint_regions.indices_within_radius(points, (0, 0, 0), 1.0), [0, 1])


if __name__ == '__main__':
    unittest.main()
