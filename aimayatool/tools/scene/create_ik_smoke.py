from __future__ import absolute_import


def run_scene_create_ik_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.create_ik import build_create_ik

    cmds.file(new=True, force=True)
    parent = cmds.createNode("transform", name="RigRoot_GRP")
    world = cmds.createNode("transform", name="World_GRP")
    objects = []
    for name, position in (("Upper_CTRL", (0, 0, 0)), ("Mid_CTRL", (4, 2, 0)), ("End_CTRL", (8, 0, 0))):
        node = cmds.circle(name=name, normal=(1, 0, 0), radius=1, constructionHistory=False)[0]
        cmds.xform(node, worldSpace=True, translation=position)
        objects.append(node)
    result = build_create_ik(objects, parent, world_parent=world)
    assert result["status"] == "applied"
    assert cmds.objExists(result["system"])
    assert len(result["joints"]) == len(result["fk_joints"]) == len(result["ik_joints"]) == 3
    assert cmds.nodeType(result["ik_handle"]) == "ikHandle"
    assert cmds.objExists(result["switch_attr"])
    assert len(result["fk_controls"]) == 3
    assert len(result["origin_offsets"]) == 3 and len(result["origin_constraints"]) == 3
    assert len(result["space_constraints"]) == 2
    assert cmds.attributeQuery("Space", node=result["ik_control"], exists=True)
    assert cmds.attributeQuery("SwitchIKFK", node=result["pole_control"], exists=True)
    for node in result["joints"] + result["fk_joints"] + result["ik_joints"] + (result["ik_handle"],): assert not cmds.getAttr(node + ".visibility")
    assert build_create_ik(objects[:2], parent)["status"] == "skipped_invalid_count"
    missing = build_create_ik((objects[0], "Missing_CTRL", objects[2]), parent)
    assert missing["status"] == "skipped_missing" and missing["missing"] == ("Missing_CTRL",)
    col_a = cmds.createNode("transform", name="ColA"); col_b = cmds.createNode("transform", name="ColB"); col_c = cmds.createNode("transform", name="ColC")
    cmds.xform(col_a, ws=True, t=(0, 0, 0)); cmds.xform(col_b, ws=True, t=(1, 0, 0)); cmds.xform(col_c, ws=True, t=(2, 0, 0))
    assert build_create_ik((col_a, col_b, col_c), parent)["status"] == "skipped_collinear"
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CREATE_IK_OK:3"
    print(marker)
    return marker
