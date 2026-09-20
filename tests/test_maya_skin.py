from __future__ import absolute_import

import importlib.util
import pathlib
import sys
import types
import unittest
from unittest import mock


class SkinDataManyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        maya = types.ModuleType('maya')
        cmds = types.ModuleType('maya.cmds')
        maya.cmds = cmds
        sys.modules.setdefault('maya', maya)
        sys.modules.setdefault('maya.cmds', cmds)
        path = pathlib.Path(__file__).parents[1] / 'aimayatool' / 'maya' / 'skin.py'
        spec = importlib.util.spec_from_file_location('aibridge_test_skin', str(path))
        cls.skin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.skin)

    def test_batches_once_per_unique_mesh_and_preserves_order(self):
        calls = []
        def fake_skin_data(mesh):
            calls.append(mesh)
            return {'mesh': mesh, 'skin_cluster': mesh + 'Skin', 'influences': [mesh + 'Joint']}
        with mock.patch.object(self.skin, 'skin_data', side_effect=fake_skin_data):
            result = self.skin.skin_data_many(['meshA.vtx[1]', 'meshA.vtx[2]', 'meshB.vtx[0]', 'meshA'])
        self.assertEqual(calls, ['meshA', 'meshB'])
        self.assertEqual([item['mesh'] for item in result], ['meshA', 'meshA', 'meshB', 'meshA'])

    def test_returns_independent_result_dicts(self):
        with mock.patch.object(self.skin, 'skin_data', return_value={'mesh': 'meshA', 'skin_cluster': 'skin', 'influences': ['joint']}):
            result = self.skin.skin_data_many(['meshA.vtx[0]', 'meshA.vtx[1]'])
        self.assertIsNot(result[0], result[1])
        result[0]['mesh'] = 'changed'
        self.assertEqual(result[1]['mesh'], 'meshA')

    def test_empty_input(self):
        self.assertEqual(self.skin.skin_data_many([]), [])
        self.assertEqual(self.skin.skin_data_many(None), [])


if __name__ == '__main__':
    unittest.main()
