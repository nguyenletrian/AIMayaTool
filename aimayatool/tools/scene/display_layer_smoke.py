from __future__ import absolute_import

import maya.cmds as cmds

from .display_layers import add_members, ensure_display_layer, members, remove_members, set_display_type, set_visibility


def run_scene_display_layer_smoke():
    cube = cmds.polyCube(name="AIMayaTool_DisplayLayerCube")[0]
    sphere = cmds.polySphere(name="AIMayaTool_DisplayLayerSphere")[0]
    layer = ensure_display_layer("AIMayaTool_DisplayLayer", [cube])
    assert cube in members(layer)
    add_members(layer, [sphere])
    current = members(layer)
    assert cube in current and sphere in current
    assert set_visibility(layer, False) is False
    assert cmds.getAttr(layer + ".visibility") is False
    assert set_visibility(layer, True) is True
    assert set_display_type(layer, 2) == 2
    assert cmds.getAttr(layer + ".displayType") == 2
    remove_members(layer, [sphere])
    assert sphere not in members(layer)
    return "SCENE_DISPLAY_LAYER_SMOKE_OK"
