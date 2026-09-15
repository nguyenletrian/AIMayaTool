from __future__ import absolute_import


def run_scene_parent_objects_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.parent_objects import parent_objects
    cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="Root_GRP")
    a = cmds.createNode("transform", name="A_CTRL")
    b = cmds.createNode("transform", name="B_CTRL")
    results = parent_objects((a, b, "Missing_CTRL"), parent=root)
    assert [item["status"] for item in results] == ["parented", "parented", "skipped_missing"]
    assert (cmds.listRelatives(a, parent=True) or [None])[0] == root
    assert (cmds.listRelatives(b, parent=True) or [None])[0] == root
    world = parent_objects((a,), world=True)
    assert world[0]["status"] == "parented" and not (cmds.listRelatives(a, parent=True) or [])
    assert parent_objects((root,), parent=root)[0]["status"] == "skipped_self_parent"
    try:
        parent_objects((a,), parent="MissingParent_GRP")
    except ValueError:
        pass
    else:
        raise AssertionError("Missing parent must raise ValueError")
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_PARENT_OBJECTS_OK:3"
    print(marker)
    return marker
