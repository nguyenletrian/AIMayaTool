from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spline_controls as spline_controls_module


def _spline_controls():
    return importlib.reload(spline_controls_module)


def run_setup_spline_controls_smoke():
    spline_controls = _spline_controls()
    cmds.file(new=True, force=True)
    curve = cmds.curve(degree=3, point=[(0, 0, 0), (3, 2, 0), (7, -1, 0), (10, 0, 0)], name="splineControlsCurve")
    result = spline_controls.create_spline_curve_controls(curve, 4, name_prefix="splineControlsTest")
    if len(result["control_joints"]) != 4 or len(result["controls"]) != 4 or not cmds.objExists(result["skin_cluster"]):
        raise RuntimeError("Spline control layer nodes were not created as expected.")
    for node in list(result["control_joints"]) + list(result["controls"]) + list(result["zero_groups"]):
        if not cmds.objExists(node):
            raise RuntimeError("Spline control layer node missing: {0}".format(node))
    before = cmds.pointPosition(curve + ".cv[1]", world=True)
    cmds.move(0, 3, 0, result["controls"][1], relative=True, worldSpace=True)
    cmds.dgdirty(allPlugs=True)
    after = cmds.pointPosition(curve + ".cv[1]", world=True)
    if sum(abs(a - b) for a, b in zip(before, after)) < 1e-4:
        raise RuntimeError("Spline curve did not deform after moving an animator control.")
    return "SETUP_SPLINE_CONTROLS_SMOKE_OK:4"
