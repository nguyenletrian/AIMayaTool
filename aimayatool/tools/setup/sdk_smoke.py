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


def run_setup_sdk_proxy_attr_smoke():
    sdk = _sdk()
    cmds.file(new=True, force=True)
    driver = cmds.createNode("transform", name="sdkProxyDriver")
    driven = cmds.createNode("transform", name="sdkProxyDriven")
    cmds.addAttr(driver, longName="drive", attributeType="double", keyable=True)
    cmds.addAttr(driven, longName="custom", attributeType="double", keyable=True)
    result = sdk.apply_driven_key_map(
        driver + ".drive",
        [
            {"driver_value": 0.0, "driven_values": {driven + ".custom": 1.0}},
            {"driver_value": 10.0, "driven_values": {driven + ".custom": 7.0}},
        ],
        use_sdk_groups=True,
        proxy_custom_attrs=True,
    )
    group = result["sdk_groups"].get(driven)
    if not group or not cmds.objExists(group + ".custom"):
        raise RuntimeError("SDK proxy custom attribute was not created.")
    incoming = cmds.listConnections(driven + ".custom", source=True, destination=False, plugs=True) or []
    if group + ".custom" not in incoming:
        raise RuntimeError("SDK proxy custom attribute was not connected to driven plug.")
    curves = cmds.listConnections(group + ".custom", source=True, destination=False, type="animCurve") or []
    if not curves:
        raise RuntimeError("Driven-key animCurve was not created on SDK proxy attribute.")
    cmds.setAttr(driver + ".drive", 10.0)
    value = cmds.getAttr(driven + ".custom")
    if abs(value - 7.0) > 1e-5:
        raise RuntimeError("SDK proxy custom attribute evaluation mismatch: {0}".format(value))
    return "SETUP_SDK_PROXY_ATTR_SMOKE_OK:1"


def run_setup_modulo_sdk_smoke():
    sdk = _sdk()
    cmds.file(new=True, force=True)
    driver = cmds.createNode("transform", name="moduloDriver")
    driven = cmds.createNode("transform", name="moduloDriven")
    cmds.addAttr(driver, longName="mode", attributeType="long", defaultValue=0, keyable=True)
    result = sdk.apply_modulo_map(
        driver + ".mode",
        {
            0: {driven + ".translateX": 1.0},
            1: {driven + ".translateX": 5.0},
            2: {driven + ".translateX": 9.0},
        },
        expression_name="moduloSDK_EXPR",
    )
    groups = list(result["sdk_groups"].values())
    if len(groups) != 1 or not cmds.objExists(groups[0]):
        raise RuntimeError("Modulo SDK group was not created or reused as expected.")
    if not cmds.objExists(result["expression"]):
        raise RuntimeError("Modulo SDK expression was not created.")
    cmds.setAttr(driver + ".mode", 4)
    cmds.dgdirty(allPlugs=True)
    value = cmds.getAttr(groups[0] + ".translateX")
    if abs(value - 5.0) > 1e-5:
        raise RuntimeError("Modulo SDK evaluation mismatch: {0}".format(value))
    cmds.setAttr(driver + ".mode", -2)
    cmds.dgdirty(allPlugs=True)
    value = cmds.getAttr(groups[0] + ".translateX")
    if abs(value - 9.0) > 1e-5:
        raise RuntimeError("Negative modulo SDK evaluation mismatch: {0}".format(value))
    return "SETUP_MODULO_SDK_SMOKE_OK:3"
