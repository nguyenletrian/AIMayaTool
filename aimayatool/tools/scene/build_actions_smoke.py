from __future__ import absolute_import

import maya.cmds as cmds

from .build_actions import ensure_hierarchy, parent_nodes


def run_scene_build_actions_smoke():
    hierarchy = ensure_hierarchy("AIMayaTool_ROOT|AIMayaTool_GEO|AIMayaTool_BODY")
    assert hierarchy == ["AIMayaTool_ROOT", "AIMayaTool_GEO", "AIMayaTool_BODY"]
    cube = cmds.polyCube(name="AIMayaTool_BuildCube")[0]
    cmds.xform(cube, worldSpace=True, translation=[3.0, 4.0, 5.0])
    before = cmds.xform(cube, query=True, worldSpace=True, translation=True)
    parent_nodes([cube], "AIMayaTool_BODY")
    after = cmds.xform(cube, query=True, worldSpace=True, translation=True)
    assert before == after
    assert (cmds.listRelatives(cube, parent=True, fullPath=False) or []) == ["AIMayaTool_BODY"]
    return "SCENE_BUILD_ACTIONS_SMOKE_OK"
