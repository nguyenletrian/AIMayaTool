from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spaces as spaces_module


def _spaces():
    return importlib.reload(spaces_module)


def run_setup_space_switch_smoke():
    spaces = _spaces()
    cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="spaceRoot")
    child = cmds.createNode("transform", name="spaceChild", parent=root)
    parent_a = cmds.createNode("transform", name="spaceWorld")
    parent_b = cmds.createNode("transform", name="spaceChest")
    cmds.setAttr(parent_a + ".translateX", 5.0)
    cmds.setAttr(parent_b + ".translateY", 7.0)

    result = spaces.create_space_switch(child, [parent_a, parent_b], labels=["World", "Chest"], maintain_offset=True, slide_attr="spaceBlend", slide_default=1.0)
    constraint = result["constraint"]
    if not cmds.objExists(constraint):
        raise RuntimeError("Space-switch parentConstraint was not created.")
    if result["enum_labels"] != ("World", "Chest"):
        raise RuntimeError("Unexpected space-switch enum labels.")
    if not cmds.attributeQuery("space", node=child, exists=True) or not cmds.attributeQuery("spaceBlend", node=child, exists=True):
        raise RuntimeError("Space-switch attributes were not created.")
    if len(result["conditions"]) != 2:
        raise RuntimeError("Expected two enum condition nodes.")
    if not result["slide_constraint"] or not result["slide_reverse"]:
        raise RuntimeError("Slide blend fallback network was not created.")

    cmds.setAttr(child + ".space", 0)
    cmds.setAttr(child + ".spaceBlend", 1.0)
    weights = cmds.parentConstraint(constraint, q=True, weightAliasList=True) or []
    if len(weights) != 2:
        raise RuntimeError("Space-switch constraint target count is unexpected.")
    if cmds.getAttr(constraint + "." + weights[0]) < 0.99 or cmds.getAttr(constraint + "." + weights[1]) > 0.01:
        raise RuntimeError("Enum index 0 did not select the first space.")
    cmds.setAttr(child + ".space", 1)
    if cmds.getAttr(constraint + "." + weights[1]) < 0.99:
        raise RuntimeError("Enum index 1 did not select the second space.")

    return "SETUP_SPACE_SWITCH_SMOKE_OK:2"
