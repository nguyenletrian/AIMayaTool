from __future__ import absolute_import


def run_scene_delete_attribute_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.delete_attribute import delete_attributes
    cmds.file(new=True, force=True)
    node = cmds.createNode("transform", name="DeleteAttr_CTRL")
    cmds.addAttr(node, longName="customA", attributeType="double", keyable=True)
    cmds.addAttr(node, longName="customB", attributeType="long", keyable=True)
    results = delete_attributes((node + ".customA", "Missing_CTRL.missing", node + ".customB"))
    assert [item["status"] for item in results] == ["deleted", "skipped_missing", "deleted"]
    assert not cmds.objExists(node + ".customA") and not cmds.objExists(node + ".customB")
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_DELETE_ATTRIBUTE_OK:2"; print(marker); return marker
