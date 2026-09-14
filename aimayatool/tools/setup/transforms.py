from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def world_matrix(node):
    """Return a node world matrix as an immutable tuple."""
    cmds = _cmds()
    _require_node(cmds, node, "Node")
    return tuple(cmds.xform(node, query=True, worldSpace=True, matrix=True))


def match_world_transform(target, source, translate=True, rotate=True, scale=False):
    """Match explicit world transform channels from source onto target."""
    cmds = _cmds()
    _require_node(cmds, target, "Target")
    _require_node(cmds, source, "Source")
    if not any((translate, rotate, scale)):
        raise ValueError("At least one transform channel must be enabled.")
    cmds.matchTransform(target, source, position=bool(translate), rotation=bool(rotate), scale=bool(scale))
    return target


def hierarchy_between(parent, child, node_type=None):
    """Return the inclusive DAG chain from parent to child, validating ancestry."""
    cmds = _cmds()
    _require_node(cmds, parent, "Parent")
    _require_node(cmds, child, "Child")
    if parent == child:
        return [parent]
    chain = [child]
    current = child
    while current != parent:
        parents = cmds.listRelatives(current, parent=True, fullPath=True) or []
        if not parents:
            raise ValueError("{0} is not a descendant of {1}".format(child, parent))
        current = parents[0]
        if node_type and cmds.nodeType(current) != node_type:
            raise ValueError("Hierarchy node has unexpected type: {0}".format(current))
        chain.append(current)
    chain.reverse()
    return chain
