from __future__ import absolute_import

import maya.cmds as cmds

from .controls import create_control, create_zero_group


def _matrix_close(a, b, tolerance=1e-5):
    return all(abs(x - y) <= tolerance for x, y in zip(a, b))


def run_setup_controls_smoke():
    cmds.file(new=True, force=True)

    target = cmds.createNode("transform", name="setupSmokeTarget")
    cmds.setAttr(target + ".translate", 3.0, 4.0, 5.0, type="double3")
    cmds.setAttr(target + ".rotate", 15.0, 25.0, 35.0, type="double3")
    expected = cmds.xform(target, query=True, worldSpace=True, matrix=True)

    control = create_control("setupSmoke_CTRL", shape="box", size=2.0, match=target)
    actual = cmds.xform(control, query=True, worldSpace=True, matrix=True)
    if not _matrix_close(expected, actual):
        raise RuntimeError("Matched control world matrix differs from target.")

    shapes = cmds.listRelatives(control, shapes=True, type="nurbsCurve") or []
    if len(shapes) != 1:
        raise RuntimeError("Expected exactly one nurbsCurve shape on control.")

    before_zero = cmds.xform(control, query=True, worldSpace=True, matrix=True)
    group, child = create_zero_group(control)
    after_zero = cmds.xform(child, query=True, worldSpace=True, matrix=True)
    if not _matrix_close(before_zero, after_zero):
        raise RuntimeError("Zero grouping changed the control world matrix.")
    if (cmds.listRelatives(child, parent=True) or [None])[0] != group:
        raise RuntimeError("Control was not parented beneath the zero group.")

    translate = cmds.getAttr(child + ".translate")[0]
    rotate = cmds.getAttr(child + ".rotate")[0]
    if any(abs(value) > 1e-5 for value in translate + rotate):
        raise RuntimeError("Zero-grouped control local translate/rotate are not zero.")

    return "SETUP_CONTROLS_SMOKE_OK"
