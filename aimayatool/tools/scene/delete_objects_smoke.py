from __future__ import absolute_import

from aimayatool.tools.scene.delete_objects import delete_objects


def run_scene_delete_objects_smoke():
    import maya.cmds as cmds

    cmds.file(new=True, force=True)
    first = cmds.createNode("transform", name="Delete_A")
    second = cmds.createNode("transform", name="Delete_B")
    results = delete_objects((first, "Missing_Delete", second))

    assert [item["status"] for item in results] == ["deleted", "skipped_missing", "deleted"]
    assert not cmds.objExists(first)
    assert not cmds.objExists(second)
    assert not cmds.objExists("Missing_Delete")

    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_DELETE_OBJECTS_OK:2"
    print(marker)
    return marker
