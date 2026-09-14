from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spaces as spaces_module


def _spaces():
    return importlib.reload(spaces_module)


def _counts():
    return {
        "transform": len(cmds.ls(type="transform") or []),
        "constraint": len(cmds.ls(type="parentConstraint") or []),
        "condition": len(cmds.ls(type="condition") or []),
    }


def _expect_value_error(fn, label):
    before = _counts()
    try:
        fn()
    except ValueError:
        after = _counts()
        if before != after:
            raise RuntimeError("{0} created partial nodes before failing: {1} -> {2}".format(label, before, after))
        return
    raise RuntimeError("{0} did not reject invalid input.".format(label))


def run_setup_space_safety_smoke():
    spaces = _spaces()
    cmds.file(new=True, force=True)

    root = cmds.createNode("transform", name="spaceSafetyRoot")
    child = cmds.createNode("transform", name="spaceSafetyChild", parent=root)
    parent_a = cmds.createNode("transform", name="spaceSafetyWorld")
    parent_b = cmds.createNode("transform", name="spaceSafetyChest")

    _expect_value_error(lambda: spaces.create_space_switch(child, [child]), "self parent")
    _expect_value_error(lambda: spaces.create_space_switch(child, [parent_a, parent_a]), "duplicate parent")
    _expect_value_error(lambda: spaces.create_space_switch(child, [parent_a, parent_b], labels=["World", "World"]), "duplicate label")
    _expect_value_error(lambda: spaces.create_space_switch(child, [parent_a], labels=[""]), "empty label")
    _expect_value_error(lambda: spaces.create_space_switch(child, [parent_a], attr_name="space", slide_attr="space"), "attribute collision")

    cmds.addAttr(child, longName="badSpace", attributeType="double", keyable=True)
    _expect_value_error(lambda: spaces.create_space_switch(child, [parent_a], attr_name="badSpace"), "existing enum type collision")

    result = spaces.create_space_switch(child, [parent_a, parent_b], labels=["World", "Chest"], slide_attr="spaceBlend")
    if result["enum_labels"] != ("World", "Chest"):
        raise RuntimeError("Valid space-switch labels changed unexpectedly.")
    if not cmds.objExists(result["constraint"]) or len(result["conditions"]) != 2:
        raise RuntimeError("Valid space-switch composition did not create expected nodes.")

    return "SETUP_SPACE_SAFETY_OK:7"
