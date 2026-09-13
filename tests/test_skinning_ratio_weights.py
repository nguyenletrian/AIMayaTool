from __future__ import absolute_import

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from aimayatool.tools.skinning import ratio_weights


class RatioWeightsTests(unittest.TestCase):
    def setUp(self):
        self.cmds = mock.Mock()
        self.patch = mock.patch.object(ratio_weights, '_cmds', return_value=self.cmds)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.cmds.skinCluster.return_value = ['jointA', 'jointB', 'jointC']

    def test_redistributes_combined_weight_by_normalized_ratio(self):
        def skin_percent(_skin, _component, **kwargs):
            if kwargs.get('query') and kwargs.get('transform') == 'jointA':
                return 0.2
            if kwargs.get('query') and kwargs.get('transform') == 'jointB':
                return 0.6
            return None
        self.cmds.skinPercent.side_effect = skin_percent
        changed = ratio_weights.apply_influence_ratios('skin1', ['mesh.vtx[0]'], ['jointA', 'jointB'], [1, 3])
        self.assertEqual(changed, ['mesh.vtx[0]'])
        self.cmds.skinPercent.assert_called_with('skin1', 'mesh.vtx[0]', transformValue=[('jointA', 0.2), ('jointB', 0.6000000000000001)], normalize=True)

    def test_skips_components_with_zero_combined_weight(self):
        self.cmds.skinPercent.return_value = 0.0
        changed = ratio_weights.apply_influence_ratios('skin1', ['mesh.vtx[0]'], ['jointA', 'jointB'], [1, 1])
        self.assertEqual(changed, [])

    def test_rejects_invalid_ratio_contract(self):
        with self.assertRaises(ValueError):
            ratio_weights.apply_influence_ratios('skin1', ['mesh.vtx[0]'], ['jointA', 'jointB'], [1])
        with self.assertRaises(ValueError):
            ratio_weights.apply_influence_ratios('skin1', ['mesh.vtx[0]'], ['jointA', 'jointB'], [0, 0])


if __name__ == '__main__':
    unittest.main()
