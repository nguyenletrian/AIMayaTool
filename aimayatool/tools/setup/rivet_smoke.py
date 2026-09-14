from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import rivet as rivet_module


def run_setup_rivet_smoke():
    rivet = importlib.reload(rivet_module)
    cmds.file(new=True, force=True)
    source = cmds.polyCreateFacet(point=[(0,0,0),(4,0,0),(0,4,0)], name="rivetSource")[0]
    child = cmds.createNode("transform", name="rivetChild")
    result = rivet.create_mesh_rivet([source + ".vtx[0]", source + ".vtx[1]", source + ".vtx[2]"], "rivetTest", child=child)
    for node in (result["plane"], result["locator"], result["point_on_surface"], result["loft"], result["child_offset"], result["child_constraint"]):
        if not node or not cmds.objExists(node):
            raise RuntimeError("Rivet node missing: {0}".format(node))
    before = cmds.xform(result["locator"], query=True, worldSpace=True, translation=True)
    cmds.move(0, 2, 0, result["plane"] + ".vtx[1]", relative=True, worldSpace=True)
    cmds.dgdirty(allPlugs=True)
    after = cmds.xform(result["locator"], query=True, worldSpace=True, translation=True)
    if max(abs(a - b) for a, b in zip(after, before)) < 1e-4:
        raise RuntimeError("Rivet locator did not follow facet deformation.")
    child_pos = cmds.xform(child, query=True, worldSpace=True, translation=True)
    if max(abs(a - b) for a, b in zip(child_pos, after)) > 1e-3:
        raise RuntimeError("Rivet child did not follow locator.")
    return "SETUP_RIVET_SMOKE_OK:2"
