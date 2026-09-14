from __future__ import absolute_import


def run_scene_aim_constraint_smoke():
    import maya.cmds as cmds

    from .aim_constraint import build_aim_constraint_plan, execute_aim_constraint_plan

    cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="Root_GRP")
    child = cmds.createNode("transform", name="arm_L_CTRL", parent=root)
    target = cmds.createNode("transform", name="AimTarget_CTRL")
    reference = cmds.createNode("transform", name="UpReference_CTRL")
    content = cmds.createNode("transform", name="ConstraintContent_GRP")

    plan = build_aim_constraint_plan({
        "child": child,
        "parent": target,
        "reference": reference,
        "mainAxis": "x",
        "secondAxis": "y",
        "maintain": True,
        "constraintContent": content,
    })
    if plan[0]["aim_vector"] != (1.0, 0.0, 0.0) or plan[0]["up_vector"] != (0.0, 1.0, 0.0):
        raise AssertionError("Signed axis mapping is incorrect.")

    result = execute_aim_constraint_plan(plan)
    if len(result) != 1 or result[0]["status"] != "applied":
        raise AssertionError("Expected one applied Aim Constraint operation.")
    item = result[0]
    parent = cmds.listRelatives(child, parent=True) or []
    if not parent or parent[0] != "arm_L_CTRL_AimGrp":
        raise AssertionError("Aim offset group was not inserted above the child.")
    if cmds.nodeType(item["constraint"]) != "aimConstraint":
        raise AssertionError("Expected an aimConstraint node.")
    constraint_parent = cmds.listRelatives(item["constraint"], parent=True) or []
    if not constraint_parent or constraint_parent[0] != content:
        raise AssertionError("Constraint node was not parented under constraintContent.")
    targets = cmds.aimConstraint(item["constraint"], query=True, targetList=True) or []
    if target not in targets:
        raise AssertionError("Aim target was not preserved.")

    world_up_source = cmds.connectionInfo(item["constraint"] + ".worldUpMatrix", sourceFromDestination=True)
    expected_world_up = reference + ".worldMatrix[0]"
    if world_up_source != expected_world_up:
        raise AssertionError("Object world-up reference was not preserved: {0}".format(world_up_source))

    skipped = execute_aim_constraint_plan(({
        "operation": "aim_constraint",
        "child": "Missing_CTRL",
        "parent": target,
        "reference": reference,
        "aim_vector": (1.0, 0.0, 0.0),
        "up_vector": (0.0, 1.0, 0.0),
        "maintain_offset": True,
        "constraint_content": "",
    },))
    if skipped != ({"child": "Missing_CTRL", "status": "skipped_missing_child"},):
        raise AssertionError("Missing legacy child must be skipped deterministically.")

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_AIM_CONSTRAINT_OK:1"
