from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def ensure_display_layer(name, members=None, empty=True):
    name = str(name or "").strip()
    if not name:
        raise ValueError("display layer name is required")
    cmds = _cmds()
    if not cmds.objExists(name):
        cmds.createDisplayLayer(name=name, empty=bool(empty))
    if members:
        add_members(name, members)
    return name


def add_members(layer, members):
    members = [str(item) for item in (members or []) if str(item).strip()]
    if not members:
        return []
    cmds = _cmds()
    if not cmds.objExists(layer):
        raise ValueError("Display layer does not exist: {0}".format(layer))
    cmds.editDisplayLayerMembers(layer, members, noRecurse=True)
    return members


def remove_members(layer, members):
    members = [str(item) for item in (members or []) if str(item).strip()]
    if not members:
        return []
    cmds = _cmds()
    if not cmds.objExists(layer):
        raise ValueError("Display layer does not exist: {0}".format(layer))
    cmds.editDisplayLayerMembers("defaultLayer", members, noRecurse=True)
    return members


def members(layer, full_names=True):
    cmds = _cmds()
    if not cmds.objExists(layer):
        raise ValueError("Display layer does not exist: {0}".format(layer))
    result = cmds.editDisplayLayerMembers(layer, query=True, fullNames=bool(full_names)) or []
    return list(result)


def set_visibility(layer, visible):
    cmds = _cmds()
    if not cmds.objExists(layer):
        raise ValueError("Display layer does not exist: {0}".format(layer))
    cmds.setAttr(layer + ".visibility", bool(visible))
    return bool(visible)


def set_display_type(layer, display_type):
    display_type = int(display_type)
    if display_type not in (0, 1, 2):
        raise ValueError("display_type must be 0, 1, or 2")
    cmds = _cmds()
    if not cmds.objExists(layer):
        raise ValueError("Display layer does not exist: {0}".format(layer))
    cmds.setAttr(layer + ".displayType", display_type)
    return display_type
