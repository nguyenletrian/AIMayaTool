import unittest

from aimayatool.tools.scene.rivet import normalize_rivet


class RivetTests(unittest.TestCase):
    def test_normalize(self):
        plan = normalize_rivet({"vertexs": "body.vtx[1]\nbody.vtx[3]\nbody.vtx[8]", "name": "Chest", "copyTransform": "ref", "child": "ctrl", "parent": "grp"})
        self.assertEqual(plan["mesh"], "body")
        self.assertEqual(plan["indices"], [1, 3, 8])
        self.assertEqual(plan["plane"], "Chest_Plane")
        self.assertEqual(plan["locator"], "Chest_Loc")
        self.assertEqual(plan["childOffset"], "ctrl_RivetOffset")

    def test_optional_fields(self):
        plan = normalize_rivet({"vertexs": ["m.vtx[0]", "m.vtx[1]", "m.vtx[2]"], "name": "R"})
        self.assertEqual(plan["copyTransform"], "")
        self.assertEqual(plan["childOffset"], "")

    def test_invalid(self):
        values = [
            {},
            {"vertexs": "m.vtx[0]\nm.vtx[1]", "name": "R"},
            {"vertexs": "m.vtx[0]\nm.vtx[1]\nn.vtx[2]", "name": "R"},
            {"vertexs": "m.vtx[0]\nbad\nm.vtx[2]", "name": "R"},
            {"vertexs": "m.vtx[0]\nm.vtx[1]\nm.vtx[2]", "name": ""},
        ]
        for value in values:
            with self.assertRaises(ValueError):
                normalize_rivet(value)


if __name__ == "__main__":
    unittest.main()
