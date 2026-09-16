from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_attr(cmds, node, attribute, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))
    plug = "{0}.{1}".format(node, attribute)
    if not cmds.objExists(plug):
        raise ValueError("Attribute does not exist: {0}".format(plug))
    return plug


def normalize_attribute_spec(attribute, attr_type="float", default=None, minimum=None, maximum=None,
                             enum=None, keyable=True, lock=False, channel_box=False):
    """Return deterministic arguments for creating one Maya attribute."""
    attribute = str(attribute or "").strip()
    if not attribute:
        raise ValueError("Attribute name is required.")
    attr_type = str(attr_type or "float").strip()
    spec = {"attribute": attribute, "attr_type": attr_type, "keyable": bool(keyable),
            "lock": bool(lock), "channel_box": bool(channel_box)}
    if default is not None: spec["default"] = default
    if minimum is not None: spec["minimum"] = minimum
    if maximum is not None: spec["maximum"] = maximum
    if enum is not None:
        if isinstance(enum, (list, tuple)): enum = ":".join(str(value) for value in enum)
        spec["enum"] = str(enum)
    return spec


def create_attribute(node, attribute, attr_type="float", default=None, minimum=None, maximum=None,
                     enum=None, keyable=True, lock=False, channel_box=False, cmds_module=None):
    """Create one explicit Maya attribute and return its plug."""
    spec = normalize_attribute_spec(attribute, attr_type, default, minimum, maximum, enum,
                                    keyable, lock, channel_box)
    cmds = cmds_module or _cmds()
    if not node or not cmds.objExists(node):
        raise ValueError("Node does not exist: {0}".format(node))
    plug = "{0}.{1}".format(node, spec["attribute"])
    if cmds.objExists(plug):
        raise ValueError("Attribute already exists: {0}".format(plug))

    kwargs = {"longName": spec["attribute"], "keyable": spec["keyable"]}
    if spec["attr_type"] == "enum":
        kwargs["attributeType"] = "enum"
        kwargs["enumName"] = spec.get("enum", "")
    elif spec["attr_type"] in ("string", "matrix"):
        kwargs["dataType"] = spec["attr_type"]
    else:
        kwargs["attributeType"] = spec["attr_type"]
    if "default" in spec and spec["attr_type"] not in ("string", "matrix"):
        kwargs["defaultValue"] = spec["default"]
    if "minimum" in spec and spec["attr_type"] not in ("string", "matrix"):
        kwargs["minValue"] = spec["minimum"]
    if "maximum" in spec and spec["attr_type"] not in ("string", "matrix"):
        kwargs["maxValue"] = spec["maximum"]
    cmds.addAttr(node, **kwargs)
    if "default" in spec and spec["attr_type"] == "string":
        cmds.setAttr(plug, spec["default"], type="string")
    cmds.setAttr(plug, lock=spec["lock"], channelBox=spec["channel_box"], keyable=spec["keyable"])
    return plug


def copy_attribute_value(source, targets, attribute):
    """Copy one explicit attribute value from source to explicit targets."""
    cmds = _cmds(); targets = list(targets or [])
    if not targets:
        raise ValueError("At least one target is required.")
    source_plug = _require_attr(cmds, source, attribute, "Source")
    target_plugs = [_require_attr(cmds, target, attribute, "Target") for target in targets]
    value = cmds.getAttr(source_plug)
    for plug in target_plugs:
        cmds.setAttr(plug, value)
    return {"source": source, "targets": tuple(targets), "attribute": attribute, "value": value}
