from __future__ import absolute_import

_DATA_TYPES = {"string", "matrix"}


def _cmds():
    import maya.cmds as cmds
    return cmds


def _optional_float(value):
    if value in (None, ""):
        return None
    return float(value)


def build_attribute_spec(name, attr_type="bool", keyable=True, lock=False, channel_box=True,
                         minimum=None, maximum=None, default=None, enum=""):
    """Normalize one legacy ScenePattern attribute descriptor without touching Maya."""
    name = str(name or "").strip()
    attr_type = str(attr_type or "").strip()
    if not name:
        raise ValueError("Attribute name is required.")
    if not attr_type:
        raise ValueError("Attribute type is required.")
    return {
        "name": name,
        "type": attr_type,
        "keyable": bool(keyable),
        "lock": bool(lock),
        "channel_box": bool(channel_box),
        "minimum": _optional_float(minimum),
        "maximum": _optional_float(maximum),
        "default": _optional_float(default),
        "enum": str(enum or ""),
    }


def create_attribute(objects, name, attr_type="bool", keyable=True, lock=False, channel_box=True,
                     minimum=None, maximum=None, default=None, enum=""):
    """Create one explicit custom attribute on each existing object, skipping existing attrs."""
    cmds = _cmds()
    spec = build_attribute_spec(name, attr_type, keyable, lock, channel_box,
                                minimum, maximum, default, enum)
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "missing"})
            continue
        if cmds.attributeQuery(spec["name"], node=obj, exists=True):
            results.append({"object": obj, "status": "exists", "plug": "{0}.{1}".format(obj, spec["name"])})
            continue

        kwargs = {"longName": spec["name"], "keyable": spec["keyable"]}
        if spec["type"] in _DATA_TYPES:
            kwargs["dataType"] = spec["type"]
        else:
            kwargs["attributeType"] = spec["type"]
        if spec["type"] == "enum":
            kwargs["enumName"] = spec["enum"]
        if spec["default"] is not None:
            kwargs["defaultValue"] = spec["default"]
        if spec["minimum"] is not None:
            kwargs["minValue"] = spec["minimum"]
        if spec["maximum"] is not None:
            kwargs["maxValue"] = spec["maximum"]

        cmds.addAttr(obj, **kwargs)
        plug = "{0}.{1}".format(obj, spec["name"])
        cmds.setAttr(plug, lock=spec["lock"])
        if not cmds.getAttr(plug, keyable=True):
            cmds.setAttr(plug, channelBox=spec["channel_box"])
        results.append({"object": obj, "status": "created", "plug": plug})
    return tuple(results)
