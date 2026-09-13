from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import skirt_parent_transfer


class SkirtParentTransferTests(unittest.TestCase):
    def _plan(self):
        return {
            'joint_parent': 'ParentJnt',
            'assignments': [
                {
                    'joint': 'SkirtA',
                    'strips': {
                        'mesh.vtx[0]': ['mesh.vtx[0]', 'mesh.vtx[4]', 'mesh.vtx[8]'],
                        'mesh.vtx[1]': ['mesh.vtx[1]', 'mesh.vtx[5]', 'mesh.vtx[8]'],
                    },
                },
                {
                    'joint': 'SkirtB',
                    'strips': {},
                },
            ],
        }

    def test_flattens_and_deduplicates_assignment_strips(self):
        calls = []

        def transfer(skin, components, source, target, normalize=True):
            calls.append((skin, list(components), source, target, normalize))
            return components[:2]

        result = skirt_parent_transfer.apply_parent_transfers('skin1', self._plan(), transfer_fn=transfer)
        self.assertEqual(calls[0][1], ['mesh.vtx[0]', 'mesh.vtx[4]', 'mesh.vtx[8]', 'mesh.vtx[1]', 'mesh.vtx[5]'])
        self.assertEqual(result[0]['changed'], ['mesh.vtx[0]', 'mesh.vtx[4]'])

    def test_passes_parent_and_target_influences(self):
        calls = []

        def transfer(skin, components, source, target, normalize=True):
            calls.append((skin, source, target, normalize))
            return []

        skirt_parent_transfer.apply_parent_transfers('skin1', self._plan(), transfer_fn=transfer, normalize=False)
        self.assertEqual(calls, [('skin1', 'ParentJnt', 'SkirtA', False)])

    def test_empty_assignment_is_reported_without_transfer_call(self):
        calls = []

        def transfer(*args, **kwargs):
            calls.append((args, kwargs))
            return []

        result = skirt_parent_transfer.apply_parent_transfers('skin1', self._plan(), transfer_fn=transfer)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result[1]['joint'], 'SkirtB')
        self.assertEqual(result[1]['components'], [])
        self.assertEqual(result[1]['changed'], [])

    def test_requires_explicit_skin_plan_parent_and_assignment_joint(self):
        with self.assertRaises(ValueError):
            skirt_parent_transfer.apply_parent_transfers('', self._plan(), transfer_fn=lambda *a, **k: [])
        with self.assertRaises(ValueError):
            skirt_parent_transfer.apply_parent_transfers('skin1', [], transfer_fn=lambda *a, **k: [])
        with self.assertRaises(ValueError):
            skirt_parent_transfer.apply_parent_transfers('skin1', {'assignments': []}, transfer_fn=lambda *a, **k: [])
        with self.assertRaises(ValueError):
            skirt_parent_transfer.apply_parent_transfers('skin1', {'joint_parent': 'P', 'assignments': [{'strips': {}}]}, transfer_fn=lambda *a, **k: [])


if __name__ == '__main__':
    unittest.main()
