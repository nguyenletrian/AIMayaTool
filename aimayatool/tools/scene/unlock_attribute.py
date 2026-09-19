from __future__ import absolute_import

TRANSFORM_ATTRS = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")


def _cmds():
    import maya.cmds as cmds
    return cmds


def unlock_attributes(items):
    """Legacy ScenePattern UnlockAttribute behavior without channelBox MEL dependency."""
    cmds = _cmds()
    results = []
    for item in tuple(items or ()):
        raw = item.get("objects", "") if isinstance(item, dict) else ""
        for obj in str(raw).splitlines():
            obj = obj.strip()
            if not obj or not cmds.objExists(obj):
                results.append({"object": obj, "status": "skipped_missing"}); continue
            changed = []
            for attr in TRANSFORM_ATTRS:
                plug = obj + "." + attr
                if not cmds.objExists(plug): continue
                cmds.setAttr(plug, lock=False, keyable=True)
                for src in cmds.listConnections(plug, source=True, destination=False, plugs=True) or []:
                    cmds.disconnectAttr(src, plug)
                changed.append(attr)
            results.append({"object": obj, "status": "unlocked", "attributes": tuple(changed)})
    return tuple(results)


def unlock_attribute_managed_maya_smoke():
    cmds = _cmds(); cmds.file(new=True, force=True)
    obj = cmds.createNode("transform", name="UnlockTarget")
    driver = cmds.createNode("transform", name="UnlockDriver")
    cmds.connectAttr(driver + ".tx", obj + ".tx", force=True)
    cmds.setAttr(obj + ".ry", lock=True, keyable=False)
    result = unlock_attributes(({"objects": obj + "\nMissingUnlockObject"},))
    disconnected = not cmds.connectionInfo(obj + ".tx", isDestination=True)
    unlocked = not cmds.getAttr(obj + ".ry", lock=True)
    keyable = cmds.getAttr(obj + ".ry", keyable=True)
    attrs_ok = result[0]["status"] == "unlocked" and len(result[0]["attributes"]) == 9
    missing = result[1]["status"] == "skipped_missing"
    success = bool(disconnected and unlocked and keyable and attrs_ok and missing)
    return "AIBRIDGE_UI_SMOKE_OK:{0}".format({"disconnected": disconnected, "unlocked": unlocked, "keyable": keyable, "attrs": attrs_ok, "missing": missing, "success": success})
