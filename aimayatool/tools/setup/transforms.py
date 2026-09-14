from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _long_name(cmds, node):
    matches = cmds.ls(node, long=True) or []
    if not matches:
        raise ValueError("Node does not exist: {0}".format(node))
    return matches[0]


def _short_name(node):
    return node.rsplit("|", 1)[-1]


def _intermediate_joint_names(source_chain, name_prefix=None):
    internal = list(source_chain[1:-1])
    if name_prefix:
        return ["{0}{1}".format(name_prefix, index + 1) for index in range(len(internal))]
    return ["{0}_copy".format(_short_name(node)) for node in internal]


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
    parent = _long_name(cmds, parent)
    child = _long_name(cmds, child)
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
    if node_type and any(cmds.nodeType(node) != node_type for node in chain):
        raise ValueError("Hierarchy contains nodes outside required type: {0}".format(node_type))
    return chain


def match_joint_chain(source_begin, source_end, destination_begin, destination_end, name_prefix=None):
    """Rebuild destination intermediate joints to match a source joint chain.

    Endpoints are preserved, intermediate destination joints are replaced, and the
    returned tuple maps destination joints to their corresponding source joints.
    """
    cmds = _cmds()
    source_chain = hierarchy_between(source_begin, source_end, node_type="joint")
    destination_chain = hierarchy_between(destination_begin, destination_end, node_type="joint")
    destination_begin = destination_chain[0]
    destination_end = destination_chain[-1]

    match_world_transform(destination_begin, source_chain[0], translate=True, rotate=False, scale=False)
    match_world_transform(destination_end, source_chain[-1], translate=True, rotate=False, scale=False)

    if len(destination_chain) > 2:
        destination_end = cmds.parent(destination_end, destination_begin, absolute=True)[0]
        cmds.delete(destination_chain[1])
        destination_begin = _long_name(cmds, destination_begin)
        destination_end = _long_name(cmds, destination_end)

    mappings = [(destination_begin, source_chain[0])]
    parent_joint = destination_begin
    names = _intermediate_joint_names(source_chain, name_prefix=name_prefix)
    for source_joint, joint_name in zip(source_chain[1:-1], names):
        joint = cmds.createNode("joint", name=joint_name)
        cmds.matchTransform(joint, source_joint, position=True, rotation=False, scale=False)
        cmds.matchTransform(joint, destination_begin, position=False, rotation=True, scale=False)
        joint = cmds.parent(joint, parent_joint, absolute=True)[0]
        parent_joint = _long_name(cmds, joint)
        mappings.append((parent_joint, source_joint))

    if source_chain[1:-1]:
        destination_end = cmds.parent(destination_end, parent_joint, absolute=True)[0]
    destination_end = _long_name(cmds, destination_end)
    match_world_transform(destination_end, source_chain[-1], translate=True, rotate=False, scale=False)
    mappings.append((destination_end, source_chain[-1]))
    return tuple(mappings)
