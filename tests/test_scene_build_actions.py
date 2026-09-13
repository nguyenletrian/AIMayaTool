import sys
import types
import unittest
from unittest import mock

from aimayatool.tools.scene import build_actions


class SceneBuildActionsTests(unittest.TestCase):
    def setUp(self):
        self.cmds = mock.Mock()
        maya = types.ModuleType("maya")
        maya.cmds = self.cmds
        self.patch = mock.patch.dict(sys.modules, {"maya": maya, "maya.cmds": self.cmds})
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_ensure_group_creates_and_parents(self):
        self.cmds.objExists.side_effect = lambda name: name == "ROOT"
        self.cmds.nodeType.return_value = "transform"
        self.cmds.group.return_value = "GEO"
        self.cmds.listRelatives.return_value = []
        self.cmds.parent.return_value = ["GEO"]
        self.assertEqual(build_actions.ensure_group("GEO", parent="ROOT"), "GEO")
        self.cmds.group.assert_called_once_with(empty=True, name="GEO")
        self.cmds.parent.assert_called_once_with("GEO", "ROOT")

    def test_ensure_hierarchy_builds_in_order(self):
        with mock.patch.object(build_actions, "ensure_group", side_effect=["ROOT", "GEO", "BODY"]) as ensure:
            self.assertEqual(build_actions.ensure_hierarchy("ROOT|GEO|BODY"), ["ROOT", "GEO", "BODY"])
        self.assertEqual(ensure.call_args_list, [mock.call("ROOT", parent=None), mock.call("GEO", parent="ROOT"), mock.call("BODY", parent="GEO")])

    def test_parent_nodes_preserves_world_by_default(self):
        self.cmds.objExists.return_value = True
        self.cmds.nodeType.return_value = "transform"
        self.cmds.parent.side_effect = [["A"], ["B"]]
        self.assertEqual(build_actions.parent_nodes(["A", "B"], "ROOT"), ["A", "B"])
        self.assertEqual(self.cmds.parent.call_args_list, [mock.call("A", "ROOT", absolute=True), mock.call("B", "ROOT", absolute=True)])


if __name__ == "__main__":
    unittest.main()
