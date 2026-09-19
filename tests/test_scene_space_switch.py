import unittest
from aimayatool.tools.scene.space_switch import plan_space_switch

class SpaceSwitchTests(unittest.TestCase):
    def test_maintain_indices(self):
        p=plan_space_switch("ctrl", ["world","body"], maintain=True)
        self.assertEqual(p["options"],["world","body"]); self.assertEqual([x["pick_index"] for x in p["targets"]],[0,1])
    def test_default_and_slide(self):
        p=plan_space_switch(["a","b"],["world","body"],enum="World;Body",attr_slide="spaceBlend",default_value=.25,maintain=False)
        self.assertEqual(p["options"],["Default","World","Body"]); self.assertEqual([x["pick_index"] for x in p["targets"]],[1,2]); self.assertEqual(p["slide_complement"],"1-slide")
    def test_invalid(self):
        for args in [("",["p"]),("c",[]),("c",["p","p"])]:
            with self.assertRaises(ValueError): plan_space_switch(*args)
        with self.assertRaises(ValueError): plan_space_switch("c",["a","b"],enum="One")
        with self.assertRaises(ValueError): plan_space_switch("c",["a"],enum="Default")
        with self.assertRaises(ValueError): plan_space_switch("c",["a"],attr_slide="blend",default_value=2)

if __name__ == "__main__": unittest.main()
