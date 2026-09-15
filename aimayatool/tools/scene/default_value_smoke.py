from __future__ import absolute_import


def run_scene_default_value_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.default_value import set_default_values
    cmds.file(new=True, force=True)
    node = cmds.createNode("transform", name="DefaultValue_CTRL")
    cmds.addAttr(node, longName="amount", attributeType="double", keyable=True)
    cmds.addAttr(node, longName="count", attributeType="long", keyable=True)
    cmds.addAttr(node, longName="label", dataType="string")
    driver = cmds.createNode("transform", name="Driver_CTRL")
    cmds.connectAttr(driver + ".translateX", node + ".amount", force=True)
    cmds.setAttr(node + ".count", lock=True)
    results = set_default_values((
        {"attribute": node + ".amount", "value": "2.5"},
        {"attribute": node + ".count", "value": "3"},
        {"attribute": node + ".label", "value": "ready"},
        {"attribute": node + ".missing", "value": "1"},
    ))
    assert [item["status"] for item in results] == ["set", "set", "set", "skipped_missing"]
    assert abs(cmds.getAttr(node + ".amount") - 2.5) < 1e-6
    assert cmds.getAttr(node + ".count") == 3 and not cmds.getAttr(node + ".count", lock=True)
    assert cmds.getAttr(node + ".label") == "ready"
    assert not cmds.connectionInfo(node + ".amount", isDestination=True)
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_DEFAULT_VALUE_OK:4"; print(marker); return marker
