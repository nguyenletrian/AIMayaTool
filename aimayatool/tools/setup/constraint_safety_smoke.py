from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import constraints as constraints_module


def _constraints():
    return importlib.reload(constraints_module)


def _expect_value_error(callable_obj, label):
    try:
        callable_obj()
    except ValueError:
        return
    raise RuntimeError("Expected ValueError for {0}.".format(label))


def run_setup_constraint_safety_smoke():
    constraints = _constraints()
    cmds.file(new=True, force=True)

    driver_a = cmds.createNode("transform", name="safetyDriverA")
    driver_b = cmds.createNode("transform", name="safetyDriverB")
    driven = cmds.createNode("transform", name="safetyDriven")
    up = cmds.createNode("transform", name="safetyUp")
    container = cmds.createNode("transform", name="safetyContainer")

    before_constraints = set(cmds.ls(type=("parentConstraint", "pointConstraint", "orientConstraint", "aimConstraint")) or [])
    before_groups = set(cmds.ls(type="transform") or [])

    _expect_value_error(lambda: constraints.create_parent_constraint([driver_a, driver_a], driven), "duplicate parent drivers")
    _expect_value_error(lambda: constraints.create_parent_constraint([driven], driven), "self parent constraint")
    _expect_value_error(lambda: constraints.create_point_constraint(driven, driven), "self point constraint")
    _expect_value_error(lambda: constraints.create_orient_constraint(driven, driven), "self orient constraint")
    _expect_value_error(lambda: constraints.create_aim_constraint(driver_a, driven, up, aim_axis="x", up_axis="-x"), "collinear aim/up axes")
    _expect_value_error(lambda: constraints.create_aim_constraint(driver_a, driven, up, aim_axis="banana", up_axis="y", use_offset_group=True), "unsupported aim axis preflight")
    _expect_value_error(lambda: constraints.create_parent_constraint([driver_a, driver_b], driven, use_offset_group=True, container="missingContainer"), "missing container preflight")

    after_constraints = set(cmds.ls(type=("parentConstraint", "pointConstraint", "orientConstraint", "aimConstraint")) or [])
    after_groups = set(cmds.ls(type="transform") or [])
    if after_constraints != before_constraints:
        raise RuntimeError("Constraint safety preflight created partial constraint nodes.")
    if after_groups != before_groups:
        raise RuntimeError("Constraint safety preflight created partial transform groups.")

    valid = constraints.create_parent_constraint([driver_a, driver_b], driven, maintain_offset=True, use_offset_group=True, container=container)
    if not cmds.objExists(valid["constraint"]) or not cmds.objExists(valid["offset_group"]):
        raise RuntimeError("Valid parent constraint composition failed after safety hardening.")
    parent = cmds.listRelatives(valid["constraint"], parent=True, fullPath=False) or []
    if parent != [container]:
        raise RuntimeError("Constraint container parenting changed after safety hardening.")

    return "SETUP_CONSTRAINT_SAFETY_OK:8"
