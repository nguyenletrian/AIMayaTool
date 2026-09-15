from __future__ import absolute_import


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
        "default": default if attr_type == "string" else _optional_float(default),
        "enum": str(enum or ""),
    }


def build_create_attribute_plan(objects, name, attr_type="bool", keyable=True, lock=False,
                                channel_box=True, minimum=None, maximum=None, default=None, enum=""):
    """Return deterministic per-object Scene composition data."""
    spec = build_attribute_spec(name, attr_type, keyable, lock, channel_box,
                                minimum, maximum, default, enum)
    return tuple({"object": obj, "spec": dict(spec)} for obj in tuple(objects or ()))


def create_attribute(objects, name, attr_type="bool", keyable=True, lock=False, channel_box=True,
                     minimum=None, maximum=None, default=None, enum="", create_attribute_fn=None):
    """Compose Scene CreateAttribute data over the reusable Setup primitive.

    Missing objects and existing attributes retain the legacy deterministic skip behavior;
    Maya attribute creation mechanics remain owned by Setup.
    """
    if create_attribute_fn is None:
        from aimayatool.tools.setup.attributes import create_attribute as create_attribute_fn
        import maya.cmds as cmds
    else:
        cmds = None
    plan = build_create_attribute_plan(objects, name, attr_type, keyable, lock, channel_box,
                                       minimum, maximum, default, enum)
    results = []
    for entry in plan:
        obj = entry["object"]
        spec = entry["spec"]
        if cmds is not None:
            if not obj or not cmds.objExists(obj):
                results.append({"object": obj, "status": "missing"})
                continue
            plug = "{0}.{1}".format(obj, spec["name"])
            if cmds.objExists(plug):
                results.append({"object": obj, "status": "exists", "plug": plug})
                continue
        try:
            plug = create_attribute_fn(
                obj, spec["name"], attr_type=spec["type"], default=spec["default"],
                minimum=spec["minimum"], maximum=spec["maximum"], enum=spec["enum"],
                keyable=spec["keyable"], lock=spec["lock"], channel_box=spec["channel_box"])
        except ValueError:
            if cmds is None:
                raise
            raise
        results.append({"object": obj, "status": "created", "plug": plug})
    return tuple(results)
