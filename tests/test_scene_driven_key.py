import unittest
from aimayatool.tools.scene.driven_key import normalize_driven_key_item,build_driven_key_plan

class DrivenKeyTests(unittest.TestCase):
    def test_normalize_and_sort(self):
        p=normalize_driven_key_item({"driverAttr":"ctrl.drive","drivenAttrs":"a.tx\nb.ry","keyData":[{"driverValue":"1","drivenValues":{"a":{"tx":"2"}}},{"driverValue":"0","drivenValues":{"b":{"ry":"3"}}}]})
        self.assertEqual([x["driverValue"] for x in p["keyData"]],[0.0,1.0]); self.assertEqual(p["offsets"]["a"],"a_SDKGrp"); self.assertEqual(p["zeroOffsets"]["b"],"b_ZeloSDKGrp")
    def test_multiple_items(self): self.assertEqual(len(build_driven_key_plan([{"driverAttr":"a.x","keyData":[{"driverValue":0,"drivenValues":{"b":{"tx":1}}}]},{"driverAttr":"c.y","keyData":[{"driverValue":0,"drivenValues":{"d":{"ry":2}}}]}])),2)
    def test_invalid(self):
        for x in [{"driverAttr":"bad","keyData":[{"driverValue":0}]},{"driverAttr":"a.x","keyData":[]},{"driverAttr":"a.x","keyData":[{"driverValue":0},{"driverValue":"0","drivenValues":{}}]}]:
            with self.assertRaises(ValueError): normalize_driven_key_item(x)

if __name__=="__main__": unittest.main()
