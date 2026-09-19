import unittest

from aimayatool.tools.scene.fold_rig import normalize_fold_rig


class FoldRigTests(unittest.TestCase):
    def test_normalize_plan(self):
        plan = normalize_fold_rig({"objEnd": "end", "objsRun": "a\nb", "destinations": "x\ny", "attrContent": "ctrl", "attr": "fold", "constraintContent": "grp"})
        self.assertEqual(plan["targets"], ["end", "x", "y"])
        self.assertEqual(plan["driverAttr"], "ctrl.fold")
        self.assertEqual(plan["count"], 2)
        self.assertEqual([x["weights"] for x in plan["keys"]], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

    def test_trims_multiline_names(self):
        plan = normalize_fold_rig({"objEnd": " end ", "objsRun": " a \n\n b ", "destinations": " x\n y ", "attrContent": " ctrl ", "attr": " fold "})
        self.assertEqual(plan["objects"], ["a", "b"])
        self.assertEqual(plan["destinations"], ["x", "y"])

    def test_rejects_invalid_input(self):
        invalid = [
            {},
            {"objEnd": "end", "objsRun": "a", "destinations": "", "attrContent": "ctrl", "attr": "fold"},
            {"objEnd": "end", "objsRun": "a\nb", "destinations": "x", "attrContent": "ctrl", "attr": "fold"},
            {"objEnd": "end", "objsRun": "a", "destinations": "x", "attrContent": "", "attr": "fold"},
        ]
        for item in invalid:
            with self.assertRaises(ValueError):
                normalize_fold_rig(item)


if __name__ == "__main__":
    unittest.main()
