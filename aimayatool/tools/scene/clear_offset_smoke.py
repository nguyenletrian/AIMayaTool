from __future__ import absolute_import


def run_scene_clear_offset_smoke():
    import maya.cmds as cmds
    from .clear_offset import apply_clear_offset

    cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="Root_GRP")
    node = cmds.createNode("transform", name="ClearOffset_CTRL", parent=root)
    cmds.setAttr(node + ".translate", 3.0, 4.0, 5.0, type="double3")
    before = cmds.xform(node, query=True, worldSpace=True, matrix=True)

    result = apply_clear_offset([node, "Missing_CTRL"])
    item = result[0]
    if item["status"] != "applied" or not item["group"].endswith("_ClearOffsetGrp"):
        raise AssertionError("Clear Offset did not create the expected offset group: {0}".format(item))
    if result[1]["status"] != "skipped_missing_object":
        raise AssertionError("Clear Offset missing-object behavior was not deterministic: {0}".format(result[1]))

    group = item["group"]
    child = item["child_path"]
    if (cmds.listRelatives(group, parent=True) or [None])[0] != root:
        raise AssertionError("Clear Offset group did not preserve the original parent.")
    if (cmds.listRelatives(child, parent=True) or [None])[0] != group:
        raise AssertionError("Clear Offset group was not inserted directly above the object.")
    after = cmds.xform(child, query=True, worldSpace=True, matrix=True)
    if [round(value, 6) for value in before] != [round(value, 6) for value in after]:
        raise AssertionError("Clear Offset did not preserve the object world transform.")

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_CLEAR_OFFSET_OK:1"
