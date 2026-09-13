from __future__ import absolute_import

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from aimayatool.tools.skinning import gradient_weights


class GradientWeightsTests(unittest.TestCase):
    def setUp(self):
        self.cmds = mock.Mock()
        self.patch = mock.patch.object(gradient_weights, '_cmds', return_value=self.cmds)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.cmds.skinCluster.return_value = ['jointA', 'jointB', 'jointC']

    def test_applies_profile_value_against_group_total(self):
        def skin_percent(_skin, _component, **kwargs):
            if kwargs.get('query'):
                return {'jointA': 0.2, 'jointB': 0.6}.get(kwargs.get('transform'), 0.0)
            return None
        self.cmds.skinPercent.side_effect = skin_percent
        changed = gradient_weights.apply_active_influence_distance_gradient(
            'skin1', ['mesh.vtx[0]'], 'jointA', ['jointA', 'jointB'], [0.0], sampler=lambda _ratio: 0.25)
        self.assertEqual(changed, ['mesh.vtx[0]'])
        self.cmds.skinPercent.assert_called_with('skin1', 'mesh.vtx[0]', transformValue=[('jointA', 0.2)], normalize=True)

    def test_passes_inverse_distance_ratios_to_sampler(self):
        seen = []
        self.cmds.skinPercent.side_effect = lambda *_args, **kwargs: 0.5 if kwargs.get('query') else None
        gradient_weights.apply_active_influence_distance_gradient(
            'skin1', ['mesh.vtx[0]', 'mesh.vtx[1]'], 'jointA', ['jointA', 'jointB'], [0.0, 10.0], sampler=lambda ratio: seen.append(ratio) or ratio)
        self.assertEqual(seen, [1.0, 0.0])

    def test_skips_zero_group_total(self):
        self.cmds.skinPercent.return_value = 0.0
        changed = gradient_weights.apply_active_influence_distance_gradient(
            'skin1', ['mesh.vtx[0]'], 'jointA', ['jointA', 'jointB'], [0.0], sampler=lambda _ratio: 1.0)
        self.assertEqual(changed, [])

    def test_rejects_invalid_contract(self):
        with self.assertRaises(ValueError):
            gradient_weights.apply_active_influence_distance_gradient('skin1', ['mesh.vtx[0]'], 'jointA', ['jointA'], [], sampler=lambda ratio: ratio)
        with self.assertRaises(ValueError):
            gradient_weights.apply_active_influence_distance_gradient('skin1', ['mesh.vtx[0]'], 'jointA', ['jointB'], [0.0], sampler=lambda ratio: ratio)


if __name__ == '__main__':
    unittest.main()
