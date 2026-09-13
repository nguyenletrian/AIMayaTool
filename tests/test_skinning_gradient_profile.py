from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import gradient_profile


class GradientProfileTests(unittest.TestCase):
    def test_inverse_distance_ratios_nearest_to_farthest(self):
        self.assertEqual(gradient_profile.inverse_distance_ratios([2.0, 4.0, 6.0]), [1.0, 0.5, 0.0])

    def test_equal_distances_match_legacy_nearest_ratio(self):
        self.assertEqual(gradient_profile.inverse_distance_ratios([3.0, 3.0]), [1.0, 1.0])

    def test_sample_distance_profile_uses_sampler(self):
        values = gradient_profile.sample_distance_profile([0.0, 5.0, 10.0], sampler=lambda ratio: ratio * ratio)
        self.assertEqual(values, [1.0, 0.25, 0.0])

    def test_rejects_negative_distance_and_out_of_range_sampler(self):
        with self.assertRaises(ValueError):
            gradient_profile.inverse_distance_ratios([0.0, -1.0])
        with self.assertRaises(ValueError):
            gradient_profile.sample_distance_profile([0.0, 1.0], sampler=lambda _ratio: 2.0)


if __name__ == '__main__':
    unittest.main()
