from __future__ import absolute_import

import importlib
import maya.cmds as cmds
from . import naming_ui


def run_setup_mirror_preview_ui_smoke():
    ui = importlib.reload(naming_ui)
    left = cmds.createNode("transform", name="arm_L_CTRL")
    right = cmds.createNode("transform", name="arm_R_CTRL")
    center = cmds.createNode("transform", name="spine_CTRL")
    cmds.xform(left, worldSpace=True, translation=(3.0, 2.0, 1.0))
    cmds.xform(right, worldSpace=True, translation=(-7.0, 5.0, 4.0))
    before = tuple(cmds.xform(right, query=True, worldSpace=True, matrix=True))
    cmds.select(left, center, replace=True)
    summary = ui._preview_mirror_selected("x")
    if summary != "1 ready, 0 missing, 1 unmapped":
        raise AssertionError("Unexpected mirror preview summary: {0}".format(summary))
    after = tuple(cmds.xform(right, query=True, worldSpace=True, matrix=True))
    if before != after:
        raise AssertionError("Mirror preview mutated the counterpart transform.")

    window = "AIMayaToolMirrorPreviewUISmoke"
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    cmds.window(window, title="AIMayaTool Mirror Preview UI Smoke")
    cmds.columnLayout(adjustableColumn=True)
    ui.build_ui()
    labels = []
    for control in cmds.lsUI(controls=True, long=True) or []:
        try:
            if cmds.objectTypeUI(control) == "button":
                labels.append(cmds.button(control, query=True, label=True))
        except Exception:
            pass
    cmds.deleteUI(window)
    missing = [label for label in ("Preview X", "Preview Y", "Preview Z", "Mirror X", "Mirror Y", "Mirror Z") if label not in labels]
    if missing:
        raise AssertionError("Mirror preview UI buttons missing: {0}".format(", ".join(missing)))
    return "SETUP_MIRROR_PREVIEW_UI_OK:3"
