from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spaces as spaces_module


def _spaces():
    return importlib.reload(spaces_module)


def _short_name(node):
    return node.rsplit("|", 1)[-1]


def _weight_map(constraint):
    targets = cmds.parentConstraint(constraint, q=True, targetList=True) or []
    weights = cmds.parentConstraint(constraint, q=True, weightAliasList=True) or []
    return dict((_short_name(target), weight) for target, weight in zip(targets, weights))


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

    # Maya may reuse/extend the existing parentConstraint when the fallback
    # root target is added to the same offset. Validate required named targets
    # instead of assuming the constraint retains exactly two aliases.
    weights = _weight_map(constraint)
    if _short_name(parent_a) not in weights or _short_name(parent_b) not in weights:
        raise RuntimeError("Space-switch parent targets are missing from the constraint.")

    cmds.setAttr(child + ".space", 0)
    cmds.setAttr(child + ".spaceBlend", 1.0)
    if cmds.getAttr(constraint + "." + weights[_short_name(parent_a)]) < 0.99 or cmds.getAttr(constraint + "." + weights[_short_name(parent_b)]) > 0.01:
        raise RuntimeError("Enum index 0 did not select the first space.")
    cmds.setAttr(child + ".space", 1)
    if cmds.getAttr(constraint + "." + weights[_short_name(parent_b)]) < 0.99:
        raise RuntimeError("Enum index 1 did not select the second space.")

    slide_weights = _weight_map(result["slide_constraint"])
    if _short_name(root) not in slide_weights:
        raise RuntimeError("Slide fallback root target is missing.")
    cmds.setAttr(child + ".spaceBlend", 0.0)
    if cmds.getAttr(result["slide_constraint"] + "." + slide_weights[_short_name(root)]) < 0.99:
        raise RuntimeError("Slide fallback did not receive inverse blend weight.")

    return "SETUP_SPACE_SWITCH_SMOKE_OK:2"
