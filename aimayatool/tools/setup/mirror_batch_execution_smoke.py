from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import naming as naming_module


def _naming():
    return importlib.reload(naming_module)


def _expect_value_error(callable_obj, label):
    try:
        callable_obj()
    except ValueError:
        return
    raise RuntimeError("Expected ValueError for {0}.".format(label))


def _world_translation(node):
    return tuple(cmds.xform(node, query=True, worldSpace=True, translation=True))


def run_setup_mirror_batch_execution_smoke():
    naming = _naming()
    cmds.file(new=True, force=True)

    root = cmds.createNode("transform", name="mirrorExecRoot")
    left_a = cmds.createNode("transform", name="Hand_L", parent=root)
    right_a = cmds.createNode("transform", name="Hand_R", parent=root)
    left_b = cmds.createNode("transform", name="Foot_L", parent=root)
    right_b = cmds.createNode("transform", name="Foot_R", parent=root)
    cmds.xform(left_a, worldSpace=True, translation=(3.0, 4.0, 5.0), rotation=(10.0, 20.0, 30.0))
    cmds.xform(left_b, worldSpace=True, translation=(-7.0, 2.0, 9.0), rotation=(-15.0, 25.0, 5.0))

    result = naming.execute_mirror_transform_batch([left_a, left_b], axis="x")
    if len(result) != 2:
        raise RuntimeError("Mirror execution did not return two applied pairs.")
    ta = _world_translation(right_a)
    tb = _world_translation(right_b)
    if any(abs(value - expected) > 1e-4 for value, expected in zip(ta, (-3.0, 4.0, 5.0))):
        raise RuntimeError("First mirrored world translation mismatch: {0}".format(ta))
    if any(abs(value - expected) > 1e-4 for value, expected in zip(tb, (7.0, 2.0, 9.0))):
        raise RuntimeError("Second mirrored world translation mismatch: {0}".format(tb))

    before_a = tuple(cmds.xform(right_a, query=True, worldSpace=True, matrix=True))
    missing = cmds.createNode("transform", name="Elbow_L", parent=root)
    _expect_value_error(lambda: naming.execute_mirror_transform_batch([left_a, missing], axis="x"), "missing later counterpart")
    after_a = tuple(cmds.xform(right_a, query=True, worldSpace=True, matrix=True))
    if after_a != before_a:
        raise RuntimeError("Missing later counterpart caused partial mutation.")

    cmds.setAttr(right_b + ".tx", lock=True)
    before_a = tuple(cmds.xform(right_a, query=True, worldSpace=True, matrix=True))
    before_b = tuple(cmds.xform(right_b, query=True, worldSpace=True, matrix=True))
    _expect_value_error(lambda: naming.execute_mirror_transform_batch([left_a, left_b], axis="x"), "locked later target")
    if tuple(cmds.xform(right_a, query=True, worldSpace=True, matrix=True)) != before_a or tuple(cmds.xform(right_b, query=True, worldSpace=True, matrix=True)) != before_b:
        raise RuntimeError("Locked later target caused partial mutation.")
    cmds.setAttr(right_b + ".tx", lock=False)

    _expect_value_error(lambda: naming.execute_mirror_transform_batch([left_a], axis="banana"), "invalid axis")
    matrix = cmds.xform(left_a, query=True, worldSpace=True, matrix=True)
    mirrored = naming.mirror_world_matrix(matrix, axis="x")
    if abs(mirrored[12] + matrix[12]) > 1e-6 or abs(mirrored[13] - matrix[13]) > 1e-6 or abs(mirrored[14] - matrix[14]) > 1e-6:
        raise RuntimeError("Pure mirror matrix helper did not reflect translation as expected.")

    return "SETUP_MIRROR_BATCH_EXECUTION_OK:7"
