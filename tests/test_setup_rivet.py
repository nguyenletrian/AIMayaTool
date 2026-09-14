from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import rivet


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"mesh", "meshShape", "child", "parent", "copy"}
        self.calls = []
    def objExists(self, name): return name in self.nodes
    def nodeType(self, node): return "mesh" if node == "meshShape" else "transform"
    def listRelatives(self, node, **kwargs):
        if kwargs.get("shapes"): return ["meshShape"] if node == "mesh" else [node + "Shape"]
        if kwargs.get("parent"): return []
        return []
    def pointPosition(self, component, world=False):
        return {"mesh.vtx[0]": (0,0,0), "mesh.vtx[1]": (1,0,0), "mesh.vtx[2]": (0,1,0)}[component]
    def polyCreateFacet(self, **kwargs): self.nodes.update({kwargs["name"], kwargs["name"] + "Shape"}); self.calls.append(("polyCreateFacet", kwargs)); return [kwargs["name"]]
    def polyEvaluate(self, node, edge=False): return 3
    def createNode(self, node_type, **kwargs):
        name = kwargs.get("name") or node_type; self.nodes.add(name); self.calls.append(("createNode", node_type, kwargs)); return name
    def setAttr(self, plug, *values, **kwargs): self.calls.append(("setAttr", plug, values, kwargs))
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def spaceLocator(self, name=None): self.nodes.add(name); self.calls.append(("spaceLocator", name)); return [name]
    def group(self, **kwargs): self.nodes.add(kwargs["name"]); self.calls.append(("group", kwargs)); return kwargs["name"]
    def xform(self, node, **kwargs):
        if kwargs.get("query") and kwargs.get("matrix"): return list(range(16))
        self.calls.append(("xform", node, kwargs))
    def parent(self, child, parent): self.calls.append(("parent", child, parent)); return [child]
    def parentConstraint(self, driver, driven, maintainOffset=True): self.calls.append(("parentConstraint", driver, driven, maintainOffset)); return ["pc"]
    def listHistory(self, node, pruneDagObjects=True): return ["skin1"]
    def ls(self, items, type=None): return ["skin1"] if type == "skinCluster" else items
    def skinCluster(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("influence"): return ["j1", "j2"]
        self.calls.append(("skinCluster", args, kwargs)); return ["planeSkin"]
    def copySkinWeights(self, **kwargs): self.calls.append(("copySkinWeights", kwargs))


class SetupRivetTests(unittest.TestCase):
    def test_requires_three_vertices_from_one_mesh(self):
        fake = FakeCmds()
        with mock.patch.object(rivet, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): rivet.create_mesh_rivet(["mesh.vtx[0]", "mesh.vtx[1]"], "r")
            with self.assertRaises(ValueError): rivet.create_mesh_rivet(["mesh.vtx[0]", "other.vtx[1]", "mesh.vtx[2]"], "r")

    def test_builds_surface_network_and_optional_bind(self):
        fake = FakeCmds()
        with mock.patch.object(rivet, "_cmds", return_value=fake):
            result = rivet.create_mesh_rivet(["mesh.vtx[0]", "mesh.vtx[1]", "mesh.vtx[2]"], "r", child="child", parent="parent", copy_transform="copy", bind_to_source=True)
        self.assertEqual("r_Plane", result["plane"])
        self.assertEqual("r_Loc", result["locator"])
        self.assertEqual("planeSkin", result["plane_skin"])
        self.assertIn(("connectAttr", "r_POSI.position", "r_Loc.translate", True), fake.calls)
        self.assertIn(("parentConstraint", "r_Loc", "child_RivetOffset", True), fake.calls)
        self.assertTrue(any(call[0] == "copySkinWeights" for call in fake.calls))


if __name__ == "__main__": unittest.main()
