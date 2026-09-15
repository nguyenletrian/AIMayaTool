from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _unlock_disconnect_chain(cmds, plug):
    node, child = plug.split(".", 1)
    plugs = [plug]
    current = child
    while True:
        parent = cmds.attributeQuery(current, node=node, listParent=True)
        if not parent:
            break
        current = parent[0]
        plugs.append(node + "." + current)
    for item in reversed(plugs):
        try:
            cmds.setAttr(item, lock=False)
        except RuntimeError:
            pass
        source = cmds.connectionInfo(item, sourceFromDestination=True)
        if source:
            cmds.disconnectAttr(source, item)


def set_default_values(items):
    """Set explicit attribute values after safely unlocking/disconnecting their compound chain."""
    cmds = _cmds()
    results = []
    for item in tuple(items or ()):
        plug = item.get("attribute") if isinstance(item, dict) else None
        value = item.get("value") if isinstance(item, dict) else None
        if not plug or "." not in plug or not cmds.objExists(plug):
            results.append({"attribute": plug, "status": "skipped_missing"}); continue
        _unlock_disconnect_chain(cmds, plug)
        attr_type = cmds.getAttr(plug, type=True)
        if attr_type in ("double", "float", "doubleAngle", "doubleLinear"):
            value = float(value)
        elif attr_type in ("long", "short", "byte", "bool", "enum"):
            value = int(value)
        if attr_type == "string":
            cmds.setAttr(plug, str(value), type="string")
        else:
            cmds.setAttr(plug, value)
        results.append({"attribute": plug, "status": "set", "type": attr_type})
    return tuple(results)
