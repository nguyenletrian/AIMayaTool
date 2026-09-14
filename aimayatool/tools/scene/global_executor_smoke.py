from __future__ import absolute_import


def _upstream_source(cmds, destination, max_depth=8):
    """Return the first non-unitConversion source driving destination."""
    source = cmds.connectionInfo(destination, sourceFromDestination=True)
    visited = set()
    for _ in range(max_depth):
        if not source:
            return source
        node = source.split(".", 1)[0]
        if node in visited or not cmds.objExists(node) or cmds.nodeType(node) != "unitConversion":
            return source
        visited.add(node)
        source = cmds.connectionInfo(node + ".input", sourceFromDestination=True)
    return source


def run_scene_global_pattern_executor_smoke():
    import maya.cmds as cmds

    from .global_executor import execute_global_pattern_plan
    from .global_plan import build_global_pattern_plan

    cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="Root_GRP")
    global_ctrl = cmds.createNode("transform", name="Global_CTRL")
    child = cmds.createNode("transform", name="arm_L_CTRL", parent=root)

    plan = build_global_pattern_plan({
        "parent": global_ctrl,
        "child": child,
        "attrSlide": "Global",
        "defaultValue": 0.25,
        "maintain": True,
    })
    result = execute_global_pattern_plan(plan)
    if len(result) != 1 or result[0]["status"] != "applied":
        raise AssertionError("Expected one applied Global ScenePattern operation.")

    item = result[0]
    offset = item["offset"]
    if not cmds.objExists(child + ".Global"):
        raise AssertionError("Global blend attribute was not created.")
    if abs(cmds.getAttr(child + ".Global") - 0.25) > 1e-6:
        raise AssertionError("Global blend default value was not preserved.")
    parent = cmds.listRelatives(child, parent=True) or []
    if not parent or parent[0] != "arm_L_CTRL_GlobalGrp":
        raise AssertionError("Global offset group was not inserted above the child.")
    if cmds.nodeType(item["blend"]) != "blendColors":
        raise AssertionError("Expected a blendColors node.")
    if cmds.nodeType(item["parent_constraint"]) != "parentConstraint":
        raise AssertionError("Expected a parentConstraint node.")
    if cmds.nodeType(item["orient_constraint"]) != "orientConstraint":
        raise AssertionError("Expected an orientConstraint node.")

    blender_source = _upstream_source(cmds, item["blend"] + ".blender")
    if blender_source != child + ".Global":
        raise AssertionError("Child Global attribute is not driving blendColors.blender: {0}".format(blender_source))

    rotate_source = _upstream_source(cmds, offset + ".rotate")
    expected_rotate_source = item["blend"] + ".output"
    if rotate_source != expected_rotate_source:
        raise AssertionError("blendColors.output is not upstream of offset.rotate: {0}".format(rotate_source))

    skipped = execute_global_pattern_plan(({
        "operation": "global_parent_blend",
        "child": "Missing_CTRL",
        "parent": global_ctrl,
        "attr_name": "Global",
        "default_value": 0.0,
        "maintain_offset": True,
    },))
    if skipped != ({"child": "Missing_CTRL", "status": "skipped_missing_child"},):
        raise AssertionError("Missing legacy children must be skipped deterministically.")

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_GLOBAL_PATTERN_EXECUTOR_OK:1"
