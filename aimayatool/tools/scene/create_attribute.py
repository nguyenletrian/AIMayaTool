from __future__ import absolute_import


def _optional_float(value):
    if value in (None, ""): return None
    return float(value)


def _objects(value):
    if isinstance(value, str): value = value.splitlines()
    return tuple(str(obj).strip() for obj in (value or ()) if str(obj).strip())


def build_attribute_spec(name, attr_type="bool", keyable=True, lock=False, channel_box=True,
                         minimum=None, maximum=None, default=None, enum=""):
    name, attr_type = str(name or "").strip(), str(attr_type or "").strip()
    if not name: raise ValueError("Attribute name is required.")
    if not attr_type: raise ValueError("Attribute type is required.")
    data_type = attr_type in ("string", "matrix")
    return {"name": name, "type": attr_type, "keyable": bool(keyable), "lock": bool(lock),
            "channel_box": bool(channel_box),
            "minimum": None if data_type else _optional_float(minimum),
            "maximum": None if data_type else _optional_float(maximum),
            "default": (str(default) if default not in (None, "") else None) if attr_type == "string"
                       else (None if attr_type == "matrix" else _optional_float(default)),
            "enum": str(enum or "") if attr_type == "enum" else ""}


def build_create_attribute_plan(objects, name, attr_type="bool", keyable=True, lock=False,
                                channel_box=True, minimum=None, maximum=None, default=None, enum=""):
    spec = build_attribute_spec(name, attr_type, keyable, lock, channel_box, minimum, maximum, default, enum)
    return tuple({"object": obj, "spec": dict(spec)} for obj in _objects(objects))


def execute_create_attribute_plan(plan, cmds_module=None, create_attribute_fn=None):
    if cmds_module is None:
        import maya.cmds as cmds
    else: cmds = cmds_module
    if create_attribute_fn is None:
        from aimayatool.tools.setup.attributes import create_attribute as create_attribute_fn
    results = []
    for entry in tuple(plan or ()):
        obj, spec = entry["object"], entry["spec"]
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing_object"}); continue
        plug = "{0}.{1}".format(obj, spec["name"])
        if cmds.objExists(plug):
            results.append({"object": obj, "status": "skipped_existing_attribute", "plug": plug}); continue
        kwargs = {"attr_type": spec["type"], "default": spec["default"], "minimum": spec["minimum"],
                  "maximum": spec["maximum"], "enum": spec["enum"], "keyable": spec["keyable"],
                  "lock": spec["lock"], "channel_box": spec["channel_box"]}
        try: plug = create_attribute_fn(obj, spec["name"], cmds_module=cmds, **kwargs)
        except TypeError: plug = create_attribute_fn(obj, spec["name"], **kwargs)
        results.append({"object": obj, "status": "created", "plug": plug})
    return tuple(results)


def create_attribute(objects, name, attr_type="bool", keyable=True, lock=False, channel_box=True,
                     minimum=None, maximum=None, default=None, enum="", cmds_module=None, create_attribute_fn=None):
    plan = build_create_attribute_plan(objects, name, attr_type, keyable, lock, channel_box,
                                       minimum, maximum, default, enum)
    return execute_create_attribute_plan(plan, cmds_module=cmds_module, create_attribute_fn=create_attribute_fn)


def clear_attribute_managed_maya_smoke_scene(cmds):
    cmds.file(new=True, force=True)
    return cmds.createNode("transform", name="AIBridge_CreateAttributeSmoke")


def create_attribute_managed_maya_smoke():
    import maya.cmds as cmds
    node = clear_attribute_managed_maya_smoke_scene(cmds)
    numeric = create_attribute([node], "weight", "double", True, False, True, 0, 1, .5, cmds_module=cmds)
    enum = create_attribute([node], "mode", "enum", False, True, True, 0, 2, 1, "FK:IK:Auto", cmds_module=cmds)
    string = create_attribute([node], "label", "string", False, False, True, default="hello", cmds_module=cmds)
    matrix = create_attribute([node], "bindMatrix", "matrix", False, False, True, cmds_module=cmds)
    existing = create_attribute([node], "weight", "double", cmds_module=cmds)
    missing = create_attribute(["AIBridge_CreateAttributeMissing"], "x", "double", cmds_module=cmds)
    numeric_ok = numeric[0]["status"] == "created" and abs(cmds.getAttr(node + ".weight") - .5) < 1e-8
    enum_ok = enum[0]["status"] == "created" and cmds.attributeQuery("mode", node=node, listEnum=True) == ["FK:IK:Auto"]
    string_ok = string[0]["status"] == "created" and cmds.getAttr(node + ".label") == "hello"
    matrix_ok = matrix[0]["status"] == "created" and cmds.getAttr(node + ".bindMatrix", type=True) == "matrix"
    existing_ok = existing[0]["status"] == "skipped_existing_attribute"
    missing_ok = missing[0]["status"] == "skipped_missing_object"
    evidence = {"numeric": numeric_ok, "enum": enum_ok, "string": string_ok, "matrix": matrix_ok,
                "existing": existing_ok, "missing": missing_ok}
    evidence["success"] = all(evidence.values())
    if not evidence["success"]: raise RuntimeError("CreateAttribute Maya smoke failed: {0}".format(evidence))
    return "AIBRIDGE_UI_SMOKE_OK:{0}".format(evidence)
