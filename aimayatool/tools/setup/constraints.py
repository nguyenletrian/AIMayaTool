from __future__ import absolute_import

from . import controls


_AXIS_VECTORS = {
    "x": (1, 0, 0), "-x": (-1, 0, 0),
    "y": (0, 1, 0), "-y": (0, -1, 0),
    "z": (0, 0, 1), "-z": (0, 0, -1),
}


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def axis_vector(axis):
    try:
        return _AXIS_VECTORS[str(axis).lower()]
    except KeyError:
        raise ValueError("Unsupported axis: {0}".format(axis))


def _constraint_target(driven, use_offset_group, suffix):
    if not use_offset_group:
        return driven, None
    group, child = controls.create_zero_group(driven, suffix=suffix)
    return group, group


def create_parent_constraint(drivers, driven, maintain_offset=True, use_offset_group=False, offset_suffix="_ParentConstraintGrp", container=None):
    """Create a multi-target parent constraint with explicit inputs and optional offset group."""
    cmds = _cmds()
    drivers = list(drivers or [])
    if not drivers:
        raise ValueError("At least one parent-constraint driver is required.")
    _require_node(cmds, driven, "Driven")
    for driver in drivers:
        _require_node(cmds, driver, "Driver")
    target, offset_group = _constraint_target(driven, use_offset_group, offset_suffix)
    constraint = cmds.parentConstraint(*(drivers + [target]), mo=bool(maintain_offset))[0]
    cmds.setAttr(constraint + ".interpType", 2)
    if container:
        _require_node(cmds, container, "Constraint container")
        cmds.parent(constraint, container)
    return {"constraint": constraint, "target": target, "offset_group": offset_group}


def create_point_constraint(driver, driven, maintain_offset=True, use_offset_group=True, offset_suffix="_PointConstraintGrp", container=None):
    """Create a point constraint, optionally on a zeroed offset group above the driven node."""
    cmds = _cmds()
    _require_node(cmds, driver, "Driver")
    _require_node(cmds, driven, "Driven")
    target, offset_group = _constraint_target(driven, use_offset_group, offset_suffix)
    constraint = cmds.pointConstraint(driver, target, mo=bool(maintain_offset))[0]
    if container:
        _require_node(cmds, container, "Constraint container")
        cmds.parent(constraint, container)
    return {"constraint": constraint, "target": target, "offset_group": offset_group}


def create_orient_constraint(driver, driven, maintain_offset=True, use_offset_group=True, offset_suffix="_OrientConstraintGrp", container=None):
    """Create an orient constraint, optionally on a zeroed offset group above the driven node."""
    cmds = _cmds()
    _require_node(cmds, driver, "Driver")
    _require_node(cmds, driven, "Driven")
    target, offset_group = _constraint_target(driven, use_offset_group, offset_suffix)
    constraint = cmds.orientConstraint(driver, target, mo=bool(maintain_offset))[0]
    if container:
        _require_node(cmds, container, "Constraint container")
        cmds.parent(constraint, container)
    return {"constraint": constraint, "target": target, "offset_group": offset_group}


def create_aim_constraint(driver, driven, world_up_object, aim_axis="x", up_axis="y", maintain_offset=True, use_offset_group=True, offset_suffix="_AimGrp", container=None):
    """Create an object-up aim constraint with configurable signed local axes."""
    cmds = _cmds()
    for node, label in ((driver, "Driver"), (driven, "Driven"), (world_up_object, "World-up object")):
        _require_node(cmds, node, label)
    target, offset_group = _constraint_target(driven, use_offset_group, offset_suffix)
    constraint = cmds.aimConstraint(driver, target, aimVector=axis_vector(aim_axis), upVector=axis_vector(up_axis), worldUpType="object", worldUpObject=world_up_object, mo=bool(maintain_offset))[0]
    if container:
        _require_node(cmds, container, "Constraint container")
        cmds.parent(constraint, container)
    return {"constraint": constraint, "target": target, "offset_group": offset_group}
