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



def _coerce_default_value(attr_type, value):
    if attr_type in ("double", "float", "doubleAngle", "doubleLinear"):
        return float(value)
    if attr_type in ("long", "short", "byte", "bool", "enum"):
        return int(value)
    if attr_type == "string":
        return str(value)
    return value

def set_default_values(items):
    """Set explicit attribute values after safely unlocking/disconnecting their compound chain."""
    cmds = _cmds()
    results = []
    for item in tuple(items or ()):
        plug = item.get("attribute") if isinstance(item, dict) else None
        value = item.get("value") if isinstance(item, dict) else None
        if not plug or "." not in plug or not cmds.objExists(plug):
            results.append({"attribute": plug, "status": "skipped_missing"}); continue
        attr_type = cmds.getAttr(plug, type=True)
        value = _coerce_default_value(attr_type, value)
        _unlock_disconnect_chain(cmds, plug)
        if attr_type == "string":
            cmds.setAttr(plug, value, type="string")
        else:
            cmds.setAttr(plug, value)
        results.append({"attribute": plug, "status": "set", "type": attr_type})
    return tuple(results)

def default_value_partial_failure_managed_maya_smoke():
    """Measure whether invalid numeric input leaves unlock/disconnect partial mutation."""
    import maya.cmds as cmds

    driver=cmds.createNode("transform",name="AIBridgeDefaultValuePartialDriver")
    target=cmds.createNode("transform",name="AIBridgeDefaultValuePartialTarget")
    cmds.addAttr(driver,longName="outValue",attributeType="double",keyable=True)
    cmds.addAttr(target,longName="value",attributeType="double",keyable=True)
    source=driver+".outValue"
    plug=target+".value"
    cmds.connectAttr(source,plug,force=True)
    cmds.setAttr(plug,lock=True)
    before_locked=bool(cmds.getAttr(plug,lock=True))
    before_source=cmds.connectionInfo(plug,sourceFromDestination=True) or ""
    error=""
    try:
        set_default_values([{"attribute":plug,"value":"not-a-number"}])
    except (TypeError,ValueError) as exc:
        error=str(exc)
    after_locked=bool(cmds.getAttr(plug,lock=True))
    after_source=cmds.connectionInfo(plug,sourceFromDestination=True) or ""
    partial_mutation=bool(before_locked!=after_locked or before_source!=after_source)
    return {
        "operation":"default_value_partial_failure",
        "caught_invalid":bool(error),
        "partial_mutation":partial_mutation,
        "before_locked":before_locked,
        "after_locked":after_locked,
        "before_source":before_source,
        "after_source":after_source,
        "error":error,
    }

