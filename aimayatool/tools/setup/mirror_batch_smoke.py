from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import naming as naming_module


def _naming():
    return importlib.reload(naming_module)


def run_setup_mirror_batch_smoke():
    naming = _naming()
    cmds.file(new=True, force=True)

    cases = {
        "arm_L_CTRL": "arm_R_CTRL",
        "L_hand_CTRL": "R_hand_CTRL",
        "hand_Left": "hand_Right",
        "RigRArm": "RigLArm",
        "LfArm": "RtArm",
        "rig:arm_L_CTRL": "rig:arm_R_CTRL",
        "|root|rig:arm_L_CTRL": "|root|rig:arm_R_CTRL",
    }
    for source, expected in cases.items():
        actual = naming.mirror_name(source)
        if actual != expected:
            raise RuntimeError("Mirror naming mismatch: {0} -> {1}, expected {2}".format(source, actual, expected))

    root_a = cmds.createNode("transform", name="charA")
    left_a = cmds.createNode("transform", name="arm_L_CTRL", parent=root_a)
    right_a = cmds.createNode("transform", name="arm_R_CTRL", parent=root_a)
    root_b = cmds.createNode("transform", name="charB")
    cmds.createNode("transform", name="arm_L_CTRL", parent=root_b)
    cmds.createNode("transform", name="arm_R_CTRL", parent=root_b)

    plan = naming.resolve_mirror_pairs([left_a])
    if len(plan) != 1 or plan[0]["target"] != cmds.ls(right_a, long=True)[0] or plan[0]["status"] != "ready":
        raise RuntimeError("Mirror pair plan did not stay within the source DAG parent.")

    missing = cmds.createNode("transform", name="leg_L_CTRL", parent=root_a)
    plan = naming.resolve_mirror_pairs([missing], require_existing=False)
    if plan[0]["status"] != "missing" or plan[0]["target"] is not None:
        raise RuntimeError("Missing mirror counterpart was not reported safely.")

    center = cmds.createNode("transform", name="spine_CTRL", parent=root_a)
    plan = naming.resolve_mirror_pairs([center], require_existing=False)
    if plan[0]["status"] != "unmapped" or plan[0]["target"] is not None:
        raise RuntimeError("Unmapped center control was not reported safely.")

    try:
        naming.resolve_mirror_pairs([left_a, left_a])
    except ValueError:
        pass
    else:
        raise RuntimeError("Duplicate batch mirror source did not fail preflight.")

    return "SETUP_MIRROR_BATCH_OK:8"
