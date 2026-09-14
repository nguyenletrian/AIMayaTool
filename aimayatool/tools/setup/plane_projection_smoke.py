from __future__ import absolute_import

import importlib
import maya.cmds as cmds
from . import plane_projection as plane_projection_module


def run_setup_plane_projection_smoke():
    plane_projection = importlib.reload(plane_projection_module); cmds.file(new=True, force=True)
    refs = []
    for name, pos in (("planeRefA", (0,0,0)), ("planeRefB", (10,0,0)), ("planeRefC", (0,0,10))):
        node = cmds.createNode("transform", name=name); cmds.xform(node, worldSpace=True, translation=pos); refs.append(node)
    control = cmds.createNode("transform", name="planeControl"); cmds.xform(control, worldSpace=True, translation=(3,7,4))
    parent = cmds.createNode("transform", name="projectedParent"); cmds.xform(parent, worldSpace=True, translation=(5,2,-3))
    projected = cmds.createNode("transform", name="planeProjected"); cmds.parent(projected, parent)
    result = plane_projection.create_plane_projection(refs, control, projected=projected, name_prefix="planeTest")
    for node in result["utility_nodes"]:
        if not node or not cmds.objExists(node): raise RuntimeError("Plane projection utility node missing: {0}".format(node))
    cmds.dgdirty(allPlugs=True)
    position = cmds.xform(projected, query=True, worldSpace=True, translation=True)
    if max(abs(position[i]-value) for i,value in enumerate((3,0,4))) > 1e-3: raise RuntimeError("Projected point mismatch: {0}".format(position))
    cmds.xform(control, worldSpace=True, translation=(6,-5,2)); cmds.dgdirty(allPlugs=True)
    position2 = cmds.xform(projected, query=True, worldSpace=True, translation=True)
    if max(abs(position2[i]-value) for i,value in enumerate((6,0,2))) > 1e-3: raise RuntimeError("Projected point did not follow control: {0}".format(position2))
    cmds.xform(refs[0], worldSpace=True, translation=(0,2,0)); cmds.xform(refs[1], worldSpace=True, translation=(10,2,0)); cmds.xform(refs[2], worldSpace=True, translation=(0,2,10)); cmds.dgdirty(allPlugs=True)
    position3 = cmds.xform(projected, query=True, worldSpace=True, translation=True)
    if max(abs(position3[i]-value) for i,value in enumerate((6,2,2))) > 1e-3: raise RuntimeError("Projected point did not follow plane references: {0}".format(position3))
    return "SETUP_PLANE_PROJECTION_SMOKE_OK:3"
