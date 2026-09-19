from __future__ import absolute_import
import unittest
from aimayatool.tools.scene import mesh_vertex

class MeshVertexTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(mesh_vertex.parse_vertex_component("body.vtx[12]"), ("body", 12))
        self.assertRaises(ValueError, mesh_vertex.parse_vertex_component, "body.e[12]")

    def test_pair_data(self):
        data = mesh_vertex.vertex_pair_data("body.vtx[1]\nbody.vtx[2]", ["body.vtx[8]", "body.vtx[9]"])
        self.assertEqual(data, {"mesh":"body","source_indices":[1,2],"target_indices":[8,9]})

    def test_validation(self):
        self.assertRaises(ValueError, mesh_vertex.vertex_pair_data, ["a.vtx[1]"], ["b.vtx[2]"])
        self.assertRaises(ValueError, mesh_vertex.vertex_pair_data, ["a.vtx[1]"], ["a.vtx[2]","a.vtx[3]"])

if __name__ == "__main__":
    unittest.main()
