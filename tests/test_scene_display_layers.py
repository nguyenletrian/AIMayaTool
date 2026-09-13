import unittest
from unittest.mock import patch

from aimayatool.tools.scene import display_layers


class FakeCmds(object):
    def __init__(self):
        self.layers = {"defaultLayer": set()}
        self.attrs = {}

    def objExists(self, name):
        return name in self.layers or name in {"cube", "sphere"}

    def createDisplayLayer(self, name, empty=True):
        self.layers[name] = set()
        return name

    def editDisplayLayerMembers(self, layer, members=None, noRecurse=True, query=False, fullNames=True):
        if query:
            values = sorted(self.layers.get(layer, set()))
            return ["|" + item for item in values] if fullNames else values
        values = [members] if isinstance(members, str) else list(members or [])
        for item in values:
            for existing in self.layers.values():
                existing.discard(item)
            self.layers.setdefault(layer, set()).add(item)
        return values

    def setAttr(self, name, value):
        self.attrs[name] = value


class SceneDisplayLayerTests(unittest.TestCase):
    def setUp(self):
        self.cmds = FakeCmds()
        self.patch = patch("aimayatool.tools.scene.display_layers._cmds", return_value=self.cmds)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_ensure_and_membership(self):
        layer = display_layers.ensure_display_layer("testLayer", ["cube"])
        self.assertEqual(layer, "testLayer")
        self.assertEqual(display_layers.members(layer), ["|cube"])
        self.assertEqual(display_layers.members(layer, full_names=False), ["cube"])
        display_layers.add_members(layer, ["sphere"])
        self.assertEqual(display_layers.members(layer), ["|cube", "|sphere"])
        display_layers.remove_members(layer, ["sphere"])
        self.assertEqual(display_layers.members(layer), ["|cube"])

    def test_visibility_and_display_type(self):
        display_layers.ensure_display_layer("testLayer")
        self.assertFalse(display_layers.set_visibility("testLayer", False))
        self.assertEqual(display_layers.set_display_type("testLayer", 2), 2)
        with self.assertRaises(ValueError):
            display_layers.set_display_type("testLayer", 4)


if __name__ == "__main__":
    unittest.main()
