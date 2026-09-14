from __future__ import absolute_import


def run_setup_preset_execution_smoke():
    import maya.cmds as cmds
    from . import preset_execution, presets

    source_a = cmds.createNode("transform", name="arm_L_jnt")
    source_b = cmds.createNode("transform", name="arm_R_jnt")
    cmds.xform(source_a, worldSpace=True, translation=(2.0, 3.0, 4.0))
    cmds.xform(source_b, worldSpace=True, translation=(-2.0, 3.0, 4.0))

    created = preset_execution.create_controls_from_preset(
        [source_a, source_b],
        presets.get_control_preset("fk"),
    )
    if len(created) != 2:
        raise AssertionError("Expected two controls, got: {0}".format(created))
    expected_names = {"arm_L_jnt_CTRL", "arm_R_jnt_CTRL"}
    if {node.rsplit("|", 1)[-1] for node in created} != expected_names:
        raise AssertionError("Unexpected control names: {0}".format(created))
    for source, control in zip((source_a, source_b), created):
        source_matrix = cmds.xform(source, query=True, worldSpace=True, matrix=True)
        control_matrix = cmds.xform(control, query=True, worldSpace=True, matrix=True)
        if any(abs(a - b) > 1e-6 for a, b in zip(source_matrix, control_matrix)):
            raise AssertionError("Preset control did not match source transform: {0}".format(control))
        shapes = cmds.listRelatives(control, shapes=True, type="nurbsCurve", fullPath=True) or []
        if not shapes:
            raise AssertionError("Preset control has no nurbsCurve shape: {0}".format(control))

    before = set(cmds.ls(type="transform") or [])
    try:
        preset_execution.create_controls_from_preset([source_a, source_a], presets.get_control_preset("fk"))
    except ValueError as exc:
        if "Duplicate source node" not in str(exc):
            raise
    else:
        raise AssertionError("Duplicate source preflight did not reject before mutation.")
    after = set(cmds.ls(type="transform") or [])
    if before != after:
        raise AssertionError("Invalid preset request mutated the scene before rejection.")

    return "SETUP_PRESET_EXECUTION_OK:5"
