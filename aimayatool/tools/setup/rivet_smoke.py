from __future__ import absolute_import

import importlib
import maya.cmds as cmds
import maya.api.OpenMaya as om

from . import rivet as rivet_module


def _world_matrix(node):
    return om.MMatrix(cmds.xform(node, query=True, worldSpace=True, matrix=True))


def _matrix_error(a, b):
    return max(abs(a[row][col] - b[row][col]) for row in range(4) for col in range(4))


def run_setup_rivet_smoke():
    rivet = importlib.reload(rivet_module)
    cmds.file(new=True, force=True)
    source = cmds.polyCreateFacet(point=[(0,0,0),(4,0,0),(0,4,0)], name="rivetSource")[0]
    child = cmds.createNode("transform", name="rivetChild")
    result = rivet.create_mesh_rivet([source + ".vtx[0]", source + ".vtx[1]", source + ".vtx[2]"], "rivetTest", child=child)
    for node in (result["plane"], result["locator"], result["point_on_surface"], result["loft"], result["child_offset"], result["child_constraint"]):
        if not node or not cmds.objExists(node):
            raise RuntimeError("Rivet node missing: {0}".format(node))

    locator_before = _world_matrix(result["locator"])
    offset_before = _world_matrix(result["child_offset"])
    child_before = _world_matrix(child)
    relative_before = offset_before * locator_before.inverse()

    cmds.move(0, 2, 0, result["plane"] + ".vtx[1]", relative=True, worldSpace=True)
    cmds.dgdirty(allPlugs=True)

    locator_after = _world_matrix(result["locator"])
    offset_after = _world_matrix(result["child_offset"])
    child_after = _world_matrix(child)
    relative_after = offset_after * locator_after.inverse()

    if _matrix_error(locator_after, locator_before) < 1e-4:
        raise RuntimeError("Rivet locator did not follow facet deformation.")
    if _matrix_error(offset_after, offset_before) < 1e-4:
        raise RuntimeError("Rivet child offset did not follow locator transform.")
    if _matrix_error(child_after, child_before) < 1e-4:
        raise RuntimeError("Rivet child did not follow constrained offset.")
    if _matrix_error(child_after, offset_after) > 1e-3:
        raise RuntimeError("Rivet child no longer matches its zeroed offset transform.")
    if _matrix_error(relative_after, relative_before) > 1e-3:
        raise RuntimeError("Rivet child offset did not preserve maintain-offset transform relationship.")
    return "SETUP_RIVET_SMOKE_OK:2"
