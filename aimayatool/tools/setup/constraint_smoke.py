from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import constraints as constraints_module


def _constraints():
    return importlib.reload(constraints_module)


def run_setup_constraint_primitives_smoke():
    constraints = _constraints()
    cmds.file(new=True, force=True)

    driver = cmds.createNode("transform", name="constraintDriver")
    driven = cmds.createNode("transform", name="constraintDriven")
    up = cmds.createNode("transform", name="constraintUp")
    cmds.setAttr(driver + ".translate", 5.0, 0.0, 0.0, type="double3")
    cmds.setAttr(up + ".translate", 0.0, 5.0, 0.0, type="double3")

    orient = constraints.create_orient_constraint(driver, driven, maintain_offset=False, use_offset_group=True)
    if not cmds.objExists(orient["constraint"]) or not orient["offset_group"]:
        raise RuntimeError("Orient constraint primitive did not create expected nodes.")

    point_driven = cmds.createNode("transform", name="pointDriven")
    point = constraints.create_point_constraint(driver, point_driven, maintain_offset=False, use_offset_group=True)
    if not cmds.objExists(point["constraint"]) or not point["offset_group"]:
        raise RuntimeError("Point constraint primitive did not create expected nodes.")

    aim_driven = cmds.createNode("transform", name="aimDriven")
    aim = constraints.create_aim_constraint(driver, aim_driven, up, aim_axis="x", up_axis="y", maintain_offset=False, use_offset_group=True)
    if not cmds.objExists(aim["constraint"]) or not aim["offset_group"]:
        raise RuntimeError("Aim constraint primitive did not create expected nodes.")

    parent_driven = cmds.createNode("transform", name="parentDriven")
    driver_b = cmds.createNode("transform", name="constraintDriverB")
    parent = constraints.create_parent_constraint([driver, driver_b], parent_driven, maintain_offset=True)
    targets = cmds.parentConstraint(parent["constraint"], query=True, targetList=True) or []
    if len(targets) != 2:
        raise RuntimeError("Parent constraint did not preserve both drivers.")

    return "SETUP_CONSTRAINT_PRIMITIVES_SMOKE_OK:4"
