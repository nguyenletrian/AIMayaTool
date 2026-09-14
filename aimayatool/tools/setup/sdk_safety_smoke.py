from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import sdk as sdk_module


def _sdk():
    return importlib.reload(sdk_module)


def _expect_value_error(callable_obj, label):
    before = set(cmds.ls(long=True) or [])
    try:
        callable_obj()
    except ValueError:
        after = set(cmds.ls(long=True) or [])
        if before != after:
            raise RuntimeError("{0} mutated the scene before failing.".format(label))
        return
    raise RuntimeError("{0} did not raise ValueError.".format(label))


def run_setup_sdk_safety_smoke():
    sdk = _sdk()
    cmds.file(new=True, force=True)
    settings = cmds.createNode("transform", name="sdkSafetySettings")
    cmds.addAttr(settings, longName="driver", attributeType="double", keyable=True)
    driven = cmds.createNode("transform", name="sdkSafetyDriven")
    other = cmds.createNode("transform", name="sdkSafetyOther")
    driver = settings + ".driver"

    _expect_value_error(
        lambda: sdk.apply_driven_key_map(driver, [
            {"driver_value": 0, "driven_values": {driven + ".tx": 0}},
            {"driver_value": 1, "driven_values": {"missingNode.tx": 1}},
        ]),
        "late missing driven key",
    )
    _expect_value_error(
        lambda: sdk.apply_driven_key_map(driver, [{"driver_value": 1, "driven_values": {driver: 1}}]),
        "self-driven key",
    )
    _expect_value_error(
        lambda: sdk.apply_driven_key_map(driver, [{"driver_value": "bad", "driven_values": {driven + ".tx": 1}}]),
        "non-numeric driver value",
    )
    _expect_value_error(
        lambda: sdk.apply_modulo_map(driver, {0: {driven + ".tx": 0}, 1: {"missingNode.tx": 1}}),
        "late missing modulo driven",
    )
    _expect_value_error(
        lambda: sdk.apply_modulo_map(driver, {0: {driver: 0}}),
        "self-driven modulo",
    )
    _expect_value_error(
        lambda: sdk.apply_modulo_map(driver, {0: {driven + ".tx": "bad"}}),
        "non-numeric modulo value",
    )

    result = sdk.apply_driven_key_map(driver, [
        {"driver_value": 0, "driven_values": {driven + ".tx": 0, other + ".ty": 1}},
        {"driver_value": 1, "driven_values": {driven + ".tx": 5, other + ".ty": 3}},
    ])
    if len(result["sdk_groups"]) != 2 or len(result["keyed_plugs"]) != 4:
        raise RuntimeError("Valid SDK composition did not create expected groups/keys.")
    driven_group = result["sdk_groups"][driven]
    other_group = result["sdk_groups"][other]
    cmds.setAttr(driver, 1)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(driven_group + ".translateX") - 5.0) > 1e-5 or abs(cmds.getAttr(other_group + ".translateY") - 3.0) > 1e-5:
        raise RuntimeError("Valid SDK composition did not evaluate expected SDK-group values.")
    driven_world = cmds.xform(driven, query=True, worldSpace=True, translation=True)
    other_world = cmds.xform(other, query=True, worldSpace=True, translation=True)
    if abs(driven_world[0] - 5.0) > 1e-5 or abs(other_world[1] - 3.0) > 1e-5:
        raise RuntimeError("Valid SDK composition did not propagate SDK-group values to driven transforms.")
    return "SETUP_SDK_SAFETY_OK:7"
