from __future__ import absolute_import

from . import controls


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_attr(cmds, plug, label):
    if not plug or "." not in plug or not cmds.objExists(plug):
        raise ValueError("{0} does not exist: {1}".format(label, plug))


def _split_plug(plug):
    node, attr = plug.rsplit(".", 1)
    return node, attr


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
    """Apply explicit serialized driven-key data.

    key_data is an iterable of dictionaries shaped as::
        {"driver_value": 0.0, "driven_values": {"node.attr": 1.0}}

    When use_sdk_groups is True, transform-channel plugs are remapped to a reusable
    SDK group above their node before keys are created.
    """
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
                if attr.startswith(("translate", "rotate", "scale")):
                    group = sdk_groups.get(node)
                    if group is None:
                        group = ensure_sdk_group(node, suffix=sdk_suffix)
                        sdk_groups[node] = group
                    target_attr = group + "." + attr
            cmds.setDrivenKeyframe(target_attr, currentDriver=driver_attr, driverValue=driver_value, value=float(value))
            cmds.keyTangent(target_attr, itt=tangent, ott=tangent)
            keyed_plugs.append(target_attr)
    return {"driver_attr": driver_attr, "sdk_groups": dict(sdk_groups), "keyed_plugs": tuple(keyed_plugs)}
