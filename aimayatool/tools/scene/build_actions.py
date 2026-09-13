from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def ensure_group(name, parent=None):
    """Return a transform group, creating it when missing."""
    cmds = _cmds()
    if cmds.objExists(name):
        if cmds.nodeType(name) != "transform":
            raise ValueError("Existing node is not a transform: {0}".format(name))
        group = name
    else:
        group = cmds.group(empty=True, name=name)
    if parent is not None:
        if not cmds.objExists(parent) or cmds.nodeType(parent) != "transform":
            raise ValueError("Parent is not a transform: {0}".format(parent))
        current = cmds.listRelatives(group, parent=True, fullPath=False) or []
        if current != [parent]:
            group = cmds.parent(group, parent)[0]
    return group


def ensure_hierarchy(path):
    """Ensure a transform hierarchy such as 'ROOT|GEO|BODY' exists."""
    if isinstance(path, str):
        names = [item for item in path.split("|") if item]
    else:
        names = list(path or [])
    if not names:
        raise ValueError("Hierarchy requires at least one transform name")
    parent = None
    result = []
    for name in names:
        node = ensure_group(name, parent=parent)
        result.append(node)
        parent = node
    return result


def parent_nodes(nodes, parent, preserve_world=True):
    """Parent existing nodes beneath a transform and return resulting names."""
    cmds = _cmds()
    if not cmds.objExists(parent) or cmds.nodeType(parent) != "transform":
        raise ValueError("Parent is not a transform: {0}".format(parent))
    result = []
    for node in nodes or []:
        if not cmds.objExists(node):
            raise ValueError("Node does not exist: {0}".format(node))
        kwargs = {"absolute": True} if preserve_world else {"relative": True}
        result.append(cmds.parent(node, parent, **kwargs)[0])
    return result


def build_scene_structure(hierarchies):
    """Build multiple deterministic transform hierarchies and return their results."""
    return [ensure_hierarchy(path) for path in hierarchies or []]
