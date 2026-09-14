from __future__ import absolute_import
import unittest
from unittest import mock
from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"|parent", "|parent|ctrl"}
        self.parents = {"|parent|ctrl": "|parent"}
        self.children = {"|parent": ["|parent|ctrl"]}
        self.calls = []

    def objExists(self, node): return node in self.nodes
    def ls(self, node, long=False): return [node] if node in self.nodes else []
    def createNode(self, node_type, name=None):
        node = "|" + name; self.nodes.add(node); self.calls.append(("createNode", node_type, name)); return node
    def matchTransform(self, target, source, **kwargs): self.calls.append(("matchTransform", target, source, kwargs))
    def listRelatives(self, node, parent=False, children=False, fullPath=False, type=None):
        if parent:
            value = self.parents.get(node); return [value] if value else []
        if children: return list(self.children.get(node, []))
        return []
    def parent(self, child, parent=None, absolute=False, world=False):
        old_parent = self.parents.get(child)
        if old_parent and child in self.children.get(old_parent, []): self.children[old_parent].remove(child)
        new_parent = None if world else parent
        if new_parent:
            name = child.rsplit("|", 1)[-1]; child_new = new_parent + "|" + name
            self.nodes.discard(child); self.nodes.add(child_new); self.parents.pop(child, None); self.parents[child_new] = new_parent
            self.children.setdefault(new_parent, []).append(child_new)
            for key, value in list(self.children.items()): self.children[key] = [child_new if item == child else item for item in value]
            self.calls.append(("parent", child, new_parent, absolute, world)); return [child_new]
        self.parents.pop(child, None); self.calls.append(("parent", child, None, absolute, world)); return [child.rsplit("|", 1)[-1]]
    def delete(self, node): self.nodes.discard(node); self.calls.append(("delete", node))


class SetupOffsetGroupTests(unittest.TestCase):
    def test_insert_offset_group_places_group_between_parent_and_node(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake): result = transforms.insert_offset_group("|parent|ctrl")
        self.assertEqual("|parent", result["parent"])
        self.assertTrue(result["group"].endswith("ctrl_fixOffset"))
        self.assertIn(("matchTransform", "|ctrl_fixOffset", "|parent|ctrl", {"position": True, "rotation": True, "scale": True}), fake.calls)

    def test_remove_offset_group_restores_child_to_original_parent(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake): inserted = transforms.insert_offset_group("|parent|ctrl"); result = transforms.remove_offset_group(inserted["group"])
        self.assertEqual("|parent", result["parent"])
        self.assertEqual(1, len(result["children"]))
        self.assertTrue(result["children"][0].endswith("|ctrl"))

    def test_missing_node_is_rejected(self):
        with mock.patch.object(transforms, "_cmds", return_value=FakeCmds()):
            with self.assertRaises(ValueError): transforms.insert_offset_group("missing")


if __name__ == "__main__": unittest.main()
