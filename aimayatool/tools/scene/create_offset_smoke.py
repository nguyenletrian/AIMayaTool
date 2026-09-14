"""Managed Maya smoke for ScenePattern Create Offset parity."""


def run_scene_create_offset_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.create_offset import apply_create_offset

    root = cmds.createNode("transform", name="Root_GRP")
    node_a = cmds.createNode("transform", name="OffsetA_CTRL", parent=root)
    node_b = cmds.createNode("transform", name="OffsetB_CTRL", parent=root)
    cmds.xform(node_a, worldSpace=True, translation=(2.0, 3.0, 4.0))
    cmds.xform(node_b, worldSpace=True, translation=(-1.0, 5.0, 2.0))
    before_a = cmds.xform(node_a, query=True, worldSpace=True, matrix=True)
    before_b = cmds.xform(node_b, query=True, worldSpace=True, matrix=True)

    results = apply_create_offset((node_a, node_b, "Missing_CTRL"), extra_name="_SceneOffset")
    assert results[0]["status"] == "applied" and results[1]["status"] == "applied", "Create Offset did not apply to existing objects."
    assert results[2]["status"] == "skipped_missing", "Missing object was not skipped."

    for node, before, result in ((node_a, before_a, results[0]), (node_b, before_b, results[1])):
        group = result["group"]
        assert group.endswith("_SceneOffset"), "Custom offset suffix was not preserved."
        assert (cmds.listRelatives(group, parent=True) or [None])[0] == root, "Original parent was not preserved."
        assert (cmds.listRelatives(node, parent=True) or [None])[0] == group, "Object was not inserted under its offset group."
        after = cmds.xform(node, query=True, worldSpace=True, matrix=True)
        assert all(abs(a - b) < 1e-6 for a, b in zip(before, after)), "Object world transform changed."

    fallback = cmds.createNode("transform", name="Fallback_CTRL", parent=root)
    fallback_result = apply_create_offset((fallback,), extra_name="")[0]
    assert fallback_result["group"].endswith("ExtraName"), "Legacy fallback suffix ExtraName was not preserved."

    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CREATE_OFFSET_OK:3"
    print(marker)
    return marker
