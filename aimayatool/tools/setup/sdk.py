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


def ensure_sdk_group(node, suffix="_SDKGrp"):
    """Return a reusable SDK offset group above node, creating it when needed."""
    cmds = _cmds()
    if not node or not cmds.objExists(node):
        raise ValueError("Driven node does not exist: {0}".format(node))
    parent = cmds.listRelatives(node, parent=True, fullPath=False) or []
    if parent and parent[0].endswith(suffix):
        return parent[0]
    return controls.create_zero_group(node, suffix=suffix)[0]


def apply_driven_key_map(driver_attr, key_data, use_sdk_groups=True, sdk_suffix="_SDKGrp", tangent="linear"):
    """Apply explicit serialized driven-key data."""
    cmds = _cmds()
    _require_attr(cmds, driver_attr, "Driver attribute")
    key_data = list(key_data or [])
    if not key_data:
        raise ValueError("At least one driven-key entry is required.")

    sdk_groups = {}
    keyed_plugs = []
    for key in key_data:
        if "driver_value" not in key:
            raise ValueError("Each driven-key entry requires driver_value.")
        driven_values = dict(key.get("driven_values") or {})
        if not driven_values:
            raise ValueError("Each driven-key entry requires driven_values.")
        driver_value = float(key["driver_value"])
        for driven_attr, value in driven_values.items():
            _require_attr(cmds, driven_attr, "Driven attribute")
            target_attr = driven_attr
            if use_sdk_groups:
                node, attr = _split_plug(driven_attr)
                if _is_transform_channel(attr):
                    group = sdk_groups.get(node)
                    if group is None:
                        group = ensure_sdk_group(node, suffix=sdk_suffix)
                        sdk_groups[node] = group
                    target_attr = group + "." + attr
            cmds.setDrivenKeyframe(target_attr, currentDriver=driver_attr, driverValue=driver_value, value=float(value))
            cmds.keyTangent(target_attr, itt=tangent, ott=tangent)
            keyed_plugs.append(target_attr)
    return {"driver_attr": driver_attr, "sdk_groups": dict(sdk_groups), "keyed_plugs": tuple(keyed_plugs)}


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
    slots = {}
    for key, values in raw.items():
        try:
            slot = int(key)
        except (TypeError, ValueError):
            raise ValueError("Modulo slot must be an integer: {0}".format(key))
        if slot < 0 or str(slot) != str(key).strip():
            raise ValueError("Modulo slot must be a non-negative integer: {0}".format(key))
        values = dict(values or {})
        if not values:
            raise ValueError("Modulo slot {0} has no driven values.".format(slot))
        slots[slot] = values
    if modulus is None:
        modulus = max(slots) + 1
    modulus = int(modulus)
    if modulus <= max(slots):
        raise ValueError("modulus must be greater than the highest slot index.")

    sdk_groups = {}
    resolved = {}
    for slot in sorted(slots):
        resolved[slot] = []
        for driven_attr, value in slots[slot].items():
            _require_attr(cmds, driven_attr, "Driven attribute")
            target_attr = driven_attr
            if use_sdk_groups:
                node, attr = _split_plug(driven_attr)
                if _is_transform_channel(attr):
                    group = sdk_groups.get(node)
                    if group is None:
                        group = ensure_sdk_group(node, suffix=sdk_suffix)
                        sdk_groups[node] = group
                    target_attr = group + "." + attr
            resolved[slot].append((target_attr, float(value)))

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
