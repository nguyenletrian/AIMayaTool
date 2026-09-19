import unittest
from aimayatool.tools.scene.modulo_sdk import normalize_modulo_sdk, modulo_slot, build_expression_plan

class ModuloSDKTests(unittest.TestCase):
    def test_new_variant_multiline_and_dynamic_count(self):
        p=build_expression_plan("driver.mod",{"a.tx\\nb.ry":{"0":"1","2":"3"}})
        self.assertEqual(p["modulo_count"],3); self.assertEqual(len(p["assignments"][2]),2)
    def test_modulo_semantics(self):
        self.assertEqual(modulo_slot(12.9,3),0); self.assertEqual(modulo_slot(-5,3),1)
    def test_invalid(self):
        for driver,data in [("bad",{"a.tx":{"0":"1"}}),("d.a",{}),("d.a",{"a.tx":{"10":"1"}})]:
            with self.assertRaises(ValueError): normalize_modulo_sdk(driver,data)

if __name__=="__main__": unittest.main()
