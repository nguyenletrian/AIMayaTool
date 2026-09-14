from __future__ import absolute_import

from . import controls


_TRANSFORM_CHANNELS = {
    "tx", "ty", "tz", "translate", "translatex", "translatey", "translatez",
    "rx", "ry", "rz", "rotate", "rotatex", "rotatey", "rotatez",
    "sx", "sy", "sz", "scale", "scalex", "scaley", "scalez",
}


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_attr(cmds, plug, label):
    if not plug or "." not in plug or not cmds.objExists(plug):
        raise ValueError("{0} does not exist: {1}".format(label, plug))


def _split_plug(plug):
    node, attr = plug.rsplit(".", 1)
    return node, attr


def _is_transform_channel(attr):
    return str(attr).lower() in _TRANSFORM_CHANNELS


def _as_float(value, label):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError("{0} must be numeric: {1}".format(label, value))


def ensure_sdk_group(node, suffix="_SDKGrp"):
    """Return a reusable SDK offset group above node, creating it when needed."""
    cmds = _cmds()
    if not node or not cmds.objExists(node):
        raise ValueError("Driven node does not exist: {0}".format(node))
    parent = cmds.listRelatives(node, parent=True, fullPath=False) or []
    if parent and parent[0].endswith(suffix):
        return parent[0]
    return controls.create_zero_group(node, suffix=suffix)[0]


def _ensure_proxy_attr(cmds, group, child_plug, attr):
    """Ensure a double proxy channel exists on group and drives child_plug."""
    group_plug = group + "." + attr
    if not cmds.objExists(group_plug):
        cmds.addAttr(group, longName=attr, attributeType="double", keyable=True)
    incoming = cmds.listConnections(child_plug, source=True, destination=False, plugs=True) or []
    if group_plug not in incoming:
        cmds.connectAttr(group_plug, child_plug, force=True)
    return group_plug


def _preflight_driven_key_map(cmds, driver_attr, key_data):
    normalized = []
    for index, key in enumerate(key_data):
        if not isinstance(key, dict):
            raise ValueError("Driven-key entry {0} must be a mapping.".format(index))
        if "driver_value" not in key:
            raise ValueError("Each driven-key entry requires driver_value.")
        driven_values = dict(key.get("driven_values") or {})
        if not driven_values:
            raise ValueError("Each driven-key entry requires driven_values.")
        driver_value = _as_float(key["driver_value"], "driver_value")
        values = {}
        for driven_attr, value in driven_values.items():
            _require_attr(cmds, driven_attr, "Driven attribute")
            if driven_attr == driver_attr:
                raise ValueError("Driver attribute cannot also be driven: {0}".format(driver_attr))
            values[driven_attr] = _as_float(value, "Driven value for {0}".format(driven_attr))
        normalized.append((driver_value, values))
    return normalized


def apply_driven_key_map(driver_attr, key_data, use_sdk_groups=True, sdk_suffix="_SDKGrp", tangent="linear", proxy_custom_attrs=True):
    """Apply explicit serialized driven-key data.

    Transform channels are keyed on a reusable SDK offset group. When
    ``proxy_custom_attrs`` is enabled, non-transform numeric channels are also
    represented by same-named double attrs on that SDK group and connected to
    the original driven plug before keys are created. This preserves useful
    legacy Drivenkey behavior without UI/global-state coupling.
    """
    cmds = _cmds()
    _require_attr(cmds, driver_attr, "Driver attribute")
    key_data = list(key_data or [])
    if not key_data:
        raise ValueError("At least one driven-key entry is required.")
    normalized = _preflight_driven_key_map(cmds, driver_attr, key_data)

    sdk_groups = {}
    keyed_plugs = []
    for driver_value, driven_values in normalized:
        for driven_attr, value in driven_values.items():
            target_attr = driven_attr
            if use_sdk_groups:
                node, attr = _split_plug(driven_attr)
                group = sdk_groups.get(node)
                if _is_transform_channel(attr) or proxy_custom_attrs:
                    if group is None:
                        group = ensure_sdk_group(node, suffix=sdk_suffix)
                        sdk_groups[node] = group
                    if _is_transform_channel(attr):
                        target_attr = group + "." + attr
                    else:
                        target_attr = _ensure_proxy_attr(cmds, group, driven_attr, attr)
            cmds.setDrivenKeyframe(target_attr, currentDriver=driver_attr, driverValue=driver_value, value=value)
            cmds.keyTangent(target_attr, itt=tangent, ott=tangent)
            keyed_plugs.append(target_attr)
    return {"driver_attr": driver_attr, "sdk_groups": dict(sdk_groups), "keyed_plugs": tuple(keyed_plugs)}


def _preflight_modulo_slots(cmds, driver_attr, raw):
    slots = {}
    source_keys = {}
    for key, values in raw.items():
        try:
            slot = int(key)
        except (TypeError, ValueError):
            raise ValueError("Modulo slot must be an integer: {0}".format(key))
        if slot < 0 or str(slot) != str(key).strip():
            raise ValueError("Modulo slot must be a non-negative integer: {0}".format(key))
        if slot in slots:
            raise ValueError("Modulo slot normalizes to duplicate index {0}: {1}, {2}".format(slot, source_keys[slot], key))
        values = dict(values or {})
        if not values:
            raise ValueError("Modulo slot {0} has no driven values.".format(slot))
        normalized_values = {}
        for driven_attr, value in values.items():
            _require_attr(cmds, driven_attr, "Driven attribute")
            if driven_attr == driver_attr:
                raise ValueError("Driver attribute cannot also be driven: {0}".format(driver_attr))
            normalized_values[driven_attr] = _as_float(value, "Modulo driven value for {0}".format(driven_attr))
        slots[slot] = normalized_values
        source_keys[slot] = key
    return slots


def apply_modulo_map(driver_attr, slot_data, modulus=None, use_sdk_groups=True, sdk_suffix="_Modulo_Grp", expression_name=None):
    """Apply legacy ModuloSDK behavior from explicit slot -> driven-value mappings.

    slot_data maps non-negative integer slots to dictionaries of ``node.attr: value``.
    The integer driver is reduced with ``abs(int(driver) % modulus)`` and the
    matching slot values are assigned by one Maya expression.
    """
    cmds = _cmds()
    _require_attr(cmds, driver_attr, "Driver attribute")
    raw = dict(slot_data or {})
    if not raw:
        raise ValueError("At least one modulo slot is required.")
    slots = _preflight_modulo_slots(cmds, driver_attr, raw)
    if modulus is None:
        modulus = max(slots) + 1
    try:
        modulus = int(modulus)
    except (TypeError, ValueError):
        raise ValueError("modulus must be an integer: {0}".format(modulus))
    if modulus <= max(slots):
        raise ValueError("modulus must be greater than the highest slot index.")

    sdk_groups = {}
    resolved = {}
    for slot in sorted(slots):
        resolved[slot] = []
        for driven_attr, value in slots[slot].items():
            target_attr = driven_attr
            if use_sdk_groups:
                node, attr = _split_plug(driven_attr)
                if _is_transform_channel(attr):
                    group = sdk_groups.get(node)
                    if group is None:
                        group = ensure_sdk_group(node, suffix=sdk_suffix)
                        sdk_groups[node] = group
                    target_attr = group + "." + attr
            resolved[slot].append((target_attr, value))

    lines = ["float $val = {0};".format(driver_attr), "int $r = abs((int)$val % {0});".format(modulus)]
    for index, slot in enumerate(sorted(resolved)):
        prefix = "if" if index == 0 else "else if"
        body = " ".join("{0} = {1};".format(plug, value) for plug, value in resolved[slot])
        lines.append("{0} ($r == {1}) {{ {2} }}".format(prefix, slot, body))
    script = "\n".join(lines)
    kwargs = {"s": script, "o": "", "ae": True, "uc": "all"}
    if expression_name:
        kwargs["name"] = expression_name
    expression = cmds.expression(**kwargs)
    return {"driver_attr": driver_attr, "modulus": modulus, "sdk_groups": dict(sdk_groups), "resolved_slots": resolved, "expression": expression, "script": script}
