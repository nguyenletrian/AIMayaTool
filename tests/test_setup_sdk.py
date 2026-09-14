from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import sdk


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"driver.ctrl", "driven.tx", "driven.ty", "driven", "sdkGroup.tx", "sdkGroup.ty"}
        self.calls = []
    def objExists(self, name): return name in self.nodes
    def listRelatives(self, *args, **kwargs): return []
    def setDrivenKeyframe(self, *args, **kwargs): self.calls.append(("sdk", args, kwargs))
    def keyTangent(self, *args, **kwargs): self.calls.append(("tangent", args, kwargs))


class SetupSDKTests(unittest.TestCase):
    def test_requires_key_data(self):
        fake = FakeCmds()
        with mock.patch.object(sdk, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): sdk.apply_driven_key_map("driver.ctrl", [])

    def test_direct_driven_key_values(self):
        fake = FakeCmds()
        data = [{"driver_value": 0, "driven_values": {"driven.tx": 1}}, {"driver_value": 10, "driven_values": {"driven.tx": 5}}]
        with mock.patch.object(sdk, "_cmds", return_value=fake):
            result = sdk.apply_driven_key_map("driver.ctrl", data, use_sdk_groups=False)
        sdk_calls = [call for call in fake.calls if call[0] == "sdk"]
        self.assertEqual(2, len(sdk_calls))
        self.assertEqual(10.0, sdk_calls[1][2]["driverValue"])
        self.assertEqual(5.0, sdk_calls[1][2]["value"])
        self.assertEqual(("driven.tx", "driven.tx"), result["keyed_plugs"])

    def test_transform_channels_remap_to_reusable_sdk_group(self):
        fake = FakeCmds()
        data = [{"driver_value": 0, "driven_values": {"driven.tx": 1, "driven.ty": 2}}]
        with mock.patch.object(sdk, "_cmds", return_value=fake), mock.patch.object(sdk, "ensure_sdk_group", return_value="sdkGroup") as ensure:
            result = sdk.apply_driven_key_map("driver.ctrl", data)
        self.assertEqual(1, ensure.call_count)
        self.assertEqual("sdkGroup", result["sdk_groups"]["driven"])
        self.assertEqual(("sdkGroup.tx", "sdkGroup.ty"), result["keyed_plugs"])
        tangent_calls = [call for call in fake.calls if call[0] == "tangent"]
        self.assertTrue(all(call[2]["itt"] == "linear" and call[2]["ott"] == "linear" for call in tangent_calls))


if __name__ == "__main__": unittest.main()
