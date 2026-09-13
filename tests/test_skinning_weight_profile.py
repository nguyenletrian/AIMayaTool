from __future__ import absolute_import

import sys
import types
import unittest
from unittest import mock

from aimayatool.tools.skinning import weight_profile


class WeightProfileTests(unittest.TestCase):
    def setUp(self):
        self.cmds = mock.Mock()
        maya = types.ModuleType("maya")
        maya.cmds = self.cmds
        self.old_maya = sys.modules.get("maya")
        self.old_cmds = sys.modules.get("maya.cmds")
        sys.modules["maya"] = maya
        sys.modules["maya.cmds"] = self.cmds

    def tearDown(self):
        if self.old_maya is None:
            sys.modules.pop("maya", None)
        else:
            sys.modules["maya"] = self.old_maya
        if self.old_cmds is None:
            sys.modules.pop("maya.cmds", None)
        else:
            sys.modules["maya.cmds"] = self.old_cmds

    def _mock_api(self):
        selection = mock.Mock()
        selection.getDependNode.return_value = "MOBJECT"
        om = mock.Mock()
        om.MSelectionList.return_value = selection
        curve = mock.Mock()
        oma = mock.Mock()
        oma.MFnAnimCurve.return_value = curve
        oma.MFnAnimCurve.kTangentFlat = 10
        oma.MFnAnimCurve.kTangentLinear = 11
        return om, oma, curve

    def test_ensure_profile_creates_endpoints(self):
        self.cmds.objExists.return_value = False
        self.cmds.createNode.return_value = "Profile"
        self.cmds.keyframe.return_value = [0.0, 100.0]
        om, oma, curve = self._mock_api()
        with mock.patch.object(weight_profile, "_maya_api", return_value=(om, oma)):
            self.assertEqual(weight_profile.ensure_profile("Profile"), "Profile")
        self.cmds.createNode.assert_called_once_with("animCurveTU", name="Profile")
        self.assertEqual(self.cmds.setKeyframe.call_count, 2)
        self.assertEqual(curve.setInTangentType.call_count, 2)
        self.assertEqual(curve.setOutTangentType.call_count, 2)

    def test_sample_profile_normalizes_output(self):
        self.cmds.objExists.return_value = True
        self.cmds.getAttr.return_value = 25.0
        self.assertAlmostEqual(weight_profile.sample_profile(0.25, "Profile"), 0.25)
        self.cmds.getAttr.assert_called_once_with("Profile.output", time=25.0)

    def test_sample_profile_rejects_out_of_range_ratio(self):
        with self.assertRaises(ValueError):
            weight_profile.sample_profile(1.01, "Profile")

    def test_reset_profile_uses_openmaya_anim_tangents(self):
        self.cmds.objExists.return_value = True
        self.cmds.keyframe.side_effect = [[0.0, 50.0, 100.0], [0.0, 100.0], [0.0, 100.0]]
        om, oma, curve = self._mock_api()
        with mock.patch.object(weight_profile, "_maya_api", return_value=(om, oma)):
            self.assertEqual(weight_profile.reset_profile("Profile", outgoing="linear", incoming="flat"), "Profile")
        self.cmds.cutKey.assert_called_once_with("Profile", time=(50.0, 50.0), clear=True)
        curve.setOutTangentType.assert_called_once_with(0, 11)
        curve.setInTangentType.assert_called_once_with(1, 10)
        self.cmds.keyTangent.assert_not_called()

    def test_rejects_unsupported_tangent(self):
        with self.assertRaises(ValueError):
            weight_profile._set_tangent("Profile", 0.0, "ott", "bogus")

    def test_rejects_missing_key(self):
        self.cmds.keyframe.return_value = [0.0, 100.0]
        with self.assertRaises(ValueError):
            weight_profile._set_tangent("Profile", 50.0, "ott", "flat")


if __name__ == "__main__":
    unittest.main()
