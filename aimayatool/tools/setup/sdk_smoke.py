from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import sdk as sdk_module


def _sdk():
    return importlib.reload(sdk_module)


def run_setup_sdk_smoke():
    sdk = _sdk()
    cmds.file(new=True, force=True)
    driver = cmds.createNode("transform", name="sdkDriver")
    driven = cmds.createNode("transform", name="sdkDriven")
    cmds.addAttr(driver, longName="drive", attributeType="double", keyable=True)
    result = sdk.apply_driven_key_map(
        driver + ".drive",
        [
            {"driver_value": 0.0, "driven_values": {driven + ".translateX": 0.0}},
            {"driver_value": 10.0, "driven_values": {driven + ".translateX": 5.0}},
        ],
        use_sdk_groups=True,
    )
    groups = list(result["sdk_groups"].values())
    if len(groups) != 1 or not cmds.objExists(groups[0]):
        raise RuntimeError("SDK group was not created or reused as expected.")
    curves = cmds.listConnections(groups[0] + ".translateX", source=True, destination=False, type="animCurve") or []
    if not curves:
        raise RuntimeError("Driven-key animCurve was not created on SDK group channel.")
    cmds.setAttr(driver + ".drive", 10.0)
    value = cmds.getAttr(groups[0] + ".translateX")
    if abs(value - 5.0) > 1e-5:
        raise RuntimeError("Driven-key evaluation mismatch: {0}".format(value))
    return "SETUP_SDK_SMOKE_OK:1"
