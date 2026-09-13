import sys
import types
import unittest
from unittest import mock

from aimayatool.tools.skinning import influence_transfer


class InfluenceTransferTests(unittest.TestCase):
    def setUp(self):
        self.cmds = mock.Mock()
        maya = types.ModuleType("maya")
        maya.cmds = self.cmds
        self.patch = mock.patch.dict(sys.modules, {"maya": maya, "maya.cmds": self.cmds})
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_transfer_moves_source_into_target(self):
        self.cmds.skinCluster.return_value = ["jointA", "jointB"]

        def skin_percent(*args, **kwargs):
            if kwargs.get("query"):
                if kwargs.get("transform") == "jointA":
                    return 0.25
                if kwargs.get("transform") == "jointB":
                    return 0.5
            return None

        self.cmds.skinPercent.side_effect = skin_percent
        changed = influence_transfer.transfer_influence_weight("skin1", ["mesh.vtx[0]"], "jointA", "jointB")
        self.assertEqual(changed, ["mesh.vtx[0]"])
        self.cmds.skinPercent.assert_called_with("skin1", "mesh.vtx[0]", transformValue=[("jointA", 0.0), ("jointB", 0.75)], normalize=True)

    def test_transfer_skips_zero_source(self):
        self.cmds.skinCluster.return_value = ["jointA", "jointB"]
        self.cmds.skinPercent.return_value = 0.0
        self.assertEqual(influence_transfer.transfer_influence_weight("skin1", ["mesh.vtx[0]"], "jointA", "jointB"), [])

    def test_transfer_rejects_missing_influence(self):
        self.cmds.skinCluster.return_value = ["jointA"]
        with self.assertRaises(ValueError):
            influence_transfer.transfer_influence_weight("skin1", ["mesh.vtx[0]"], "jointA", "jointB")


if __name__ == "__main__":
    unittest.main()
