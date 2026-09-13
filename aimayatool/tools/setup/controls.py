from __future__ import absolute_import

import maya.cmds as cmds


_SHAPES = {
    "circle": [
        (1.0, 0.0, 0.0),
        (0.707, 0.0, 0.707),
        (0.0, 0.0, 1.0),
        (-0.707, 0.0, 0.707),
        (-1.0, 0.0, 0.0),
        (-0.707, 0.0, -0.707),
        (0.0, 0.0, -1.0),
        (0.707, 0.0, -0.707),
        (1.0, 0.0, 0.0),
    ],
    "box": [
        (-1.0, -1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0, -1.0, 1.0),
        (-1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (1.0, 1.0, 1.0),
        (1.0, 1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (1.0, 1.0, -1.0),
        (1.0, -1.0, -1.0),
    ],
}


def available_shapes():
    return tuple(sorted(_SHAPES))


def _scaled_points(shape, size):
    if shape not in _SHAPES:
        raise ValueError("Unsupported control shape: {0}".format(shape))
    size = float(size)
    if size <= 0.0:
        raise ValueError("Control size must be greater than zero.")
    return [(x * size, y * size, z * size) for x, y, z in _SHAPES[shape]]


def create_control(name, shape="circle", size=1.0, match=None, parent=None):
    """Create a degree-1 curve control with optional world-space matching."""
    control = cmds.curve(name=name, degree=1, point=_scaled_points(shape, size))
    if match:
        if not cmds.objExists(match):
            cmds.delete(control)
            raise ValueError("Match target does not exist: {0}".format(match))
        matrix = cmds.xform(match, query=True, worldSpace=True, matrix=True)
        cmds.xform(control, worldSpace=True, matrix=matrix)
    if parent:
        if not cmds.objExists(parent):
            cmds.delete(control)
            raise ValueError("Parent does not exist: {0}".format(parent))
        cmds.parent(control, parent)
    return control


def create_zero_group(node, suffix="_ZERO"):
    """Insert a zero group above node while preserving the node world transform."""
    if not cmds.objExists(node):
        raise ValueError("Node does not exist: {0}".format(node))
    parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
    matrix = cmds.xform(node, query=True, worldSpace=True, matrix=True)
    group_name = "{0}{1}".format(node.split("|")[-1], suffix)
    group = cmds.createNode("transform", name=group_name)
    cmds.xform(group, worldSpace=True, matrix=matrix)
    if parent:
        group = cmds.parent(group, parent[0])[0]
        cmds.xform(group, worldSpace=True, matrix=matrix)
    node = cmds.parent(node, group)[0]
    return group, node


def create_controls_for_nodes(nodes, shape="circle", size=1.0, suffix="_CTRL"):
    """Create one matched control for each explicit node."""
    result = []
    for node in nodes:
        short_name = node.split("|")[-1]
        result.append(create_control(short_name + suffix, shape=shape, size=size, match=node))
    return result
