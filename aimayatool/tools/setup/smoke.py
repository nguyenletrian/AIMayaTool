from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import controls as controls_module
from . import transforms as transforms_module


def _controls():
    return importlib.reload(controls_module)


def _transforms():
    return importlib.reload(transforms_module)


def _matrix_close(a, b, tolerance=1e-5):
    return all(abs(x - y) <= tolerance for x, y in zip(a, b))


def run_setup_controls_smoke():
    controls = _controls()
    cmds.file(new=True, force=True)

    target = cmds.createNode("transform", name="setupSmokeTarget")
    cmds.setAttr(target + ".translate", 3.0, 4.0, 5.0, type="double3")
    cmds.setAttr(target + ".rotate", 15.0, 25.0, 35.0, type="double3")
    expected = cmds.xform(target, query=True, worldSpace=True, matrix=True)

    control = controls.create_control("setupSmoke_CTRL", shape="box", size=2.0, match=target)
    actual = cmds.xform(control, query=True, worldSpace=True, matrix=True)
    if not _matrix_close(expected, actual):
        raise RuntimeError("Matched control world matrix differs from target.")

    shapes = cmds.listRelatives(control, shapes=True, type="nurbsCurve") or []
    if len(shapes) != 1:
        raise RuntimeError("Expected exactly one nurbsCurve shape on control.")

    before_zero = cmds.xform(control, query=True, worldSpace=True, matrix=True)
    group, child = controls.create_zero_group(control)
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


def run_setup_control_shape_catalog_smoke():
    controls = _controls()
    cmds.file(new=True, force=True)
    shape_names = ("cube", "sphere", "diamond", "locator", "eye")
    for shape in shape_names:
        control = controls.create_control("setupShape_{0}_CTRL".format(shape), shape=shape, size=1.0)
        shapes = cmds.listRelatives(control, shapes=True, type="nurbsCurve") or []
        if len(shapes) != 1:
            raise RuntimeError("Expected one nurbsCurve for shape {0}.".format(shape))
        cvs = cmds.ls(shapes[0] + ".cv[*]", flatten=True) or []
        if not cvs:
            raise RuntimeError("Control shape {0} has no curve CVs.".format(shape))
    return "SETUP_CONTROL_SHAPE_CATALOG_SMOKE_OK:{0}".format(len(shape_names))


def run_setup_transform_primitives_smoke():
    transforms = _transforms()
    cmds.file(new=True, force=True)

    source = cmds.createNode("transform", name="setupTransformSource")
    target = cmds.createNode("transform", name="setupTransformTarget")
    cmds.setAttr(source + ".translate", 2.0, 3.0, 4.0, type="double3")
    cmds.setAttr(source + ".rotate", 10.0, 20.0, 30.0, type="double3")
    transforms.match_world_transform(target, source, translate=True, rotate=True, scale=False)
    if not _matrix_close(transforms.world_matrix(target), transforms.world_matrix(source)):
        raise RuntimeError("Matched transform world matrix differs from source.")

    root = cmds.createNode("joint", name="setupRoot_JNT")
    mid = cmds.createNode("joint", name="setupMid_JNT", parent=root)
    end = cmds.createNode("joint", name="setupEnd_JNT", parent=mid)
    chain = transforms.hierarchy_between(cmds.ls(root, long=True)[0], cmds.ls(end, long=True)[0], node_type="joint")
    if len(chain) != 3 or not chain[1].endswith("setupMid_JNT"):
        raise RuntimeError("Joint hierarchy traversal returned an unexpected chain.")

    return "SETUP_TRANSFORM_PRIMITIVES_SMOKE_OK:3"
