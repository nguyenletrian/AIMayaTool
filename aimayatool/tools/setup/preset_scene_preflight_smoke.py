from __future__ import absolute_import


def run_setup_preset_scene_preflight_smoke():
    import maya.cmds as cmds
    from . import preset_execution

    source = cmds.createNode("transform", name="spine_M")
    preset = {"name": "fk", "shape": "circle", "size": 1.0, "suffix": "_CTRL"}

    missing_before = set(cmds.ls(type="transform", long=True) or [])
    try:
        preset_execution.create_controls_from_preset(["does_not_exist"], preset)
    except ValueError as exc:
        if "do not exist" not in str(exc):
            raise
    else:
        raise AssertionError("Missing source node was not rejected.")
    if set(cmds.ls(type="transform", long=True) or []) != missing_before:
        raise AssertionError("Missing-node preflight mutated the scene.")

    existing = cmds.createNode("transform", name="spine_M_CTRL")
    collision_before = set(cmds.ls(type="transform", long=True) or [])
    try:
        preset_execution.create_controls_from_preset([source], preset)
    except ValueError as exc:
        if "already exists" not in str(exc):
            raise
    else:
        raise AssertionError("Existing output name was not rejected.")
    if set(cmds.ls(type="transform", long=True) or []) != collision_before:
        raise AssertionError("Name-collision preflight mutated the scene.")

    cmds.delete(existing)
    controls = preset_execution.create_controls_from_preset([source], preset)
    if controls != ["spine_M_CTRL"]:
        raise AssertionError("Unexpected created controls: {0}".format(controls))
    shapes = cmds.listRelatives(controls[0], shapes=True, type="nurbsCurve") or []
    if not shapes:
        raise AssertionError("Preset execution did not create a nurbsCurve control.")

    return "SETUP_PRESET_SCENE_PREFLIGHT_OK:4"
