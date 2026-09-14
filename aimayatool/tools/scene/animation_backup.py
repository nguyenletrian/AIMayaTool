from __future__ import absolute_import

import json


def _cmds():
    import maya.cmds as cmds
    return cmds


def collect_animation_data(objects):
    """Collect animCurve key times/values for explicit objects and keyable attrs."""
    cmds = _cmds()
    data = {}
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            continue
        obj_data = {}
        for attr in cmds.listAttr(obj, keyable=True) or []:
            plug = "{0}.{1}".format(obj, attr)
            curves = cmds.listConnections(plug, source=True, destination=False, type="animCurve") or []
            if not curves:
                continue
            curve = curves[0]
            times = cmds.keyframe(curve, query=True, timeChange=True) or []
            values = cmds.keyframe(curve, query=True, valueChange=True) or []
            if times:
                obj_data[attr] = {"times": list(times), "values": list(values)}
        if obj_data:
            data[obj] = obj_data
    return data


def write_animation_backup(path, objects):
    data = collect_animation_data(objects)
    with open(path, "w") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
    return data


def read_animation_backup(path):
    with open(path, "r") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("Animation backup root must be an object.")
    return data


def apply_animation_data(data, clear_existing=True):
    """Apply serialized animation keys; missing objects/attrs are skipped deterministically."""
    cmds = _cmds()
    results = []
    for obj in sorted((data or {}).keys()):
        if not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing_object"})
            continue
        applied_attrs = []
        for attr, attr_data in sorted((data.get(obj) or {}).items()):
            plug = "{0}.{1}".format(obj, attr)
            if not cmds.objExists(plug):
                continue
            times = list((attr_data or {}).get("times") or [])
            values = list((attr_data or {}).get("values") or [])
            if not times:
                continue
            if len(times) != len(values):
                raise ValueError("Animation backup times/values length mismatch: {0}".format(plug))
            if clear_existing:
                cmds.cutKey(plug, clear=True)
            for time, value in zip(times, values):
                cmds.setKeyframe(plug, time=float(time), value=float(value))
            applied_attrs.append(attr)
        results.append({"object": obj, "status": "applied", "attributes": tuple(applied_attrs)})
    return tuple(results)


def import_animation_backup(path, clear_existing=True):
    return apply_animation_data(read_animation_backup(path), clear_existing=clear_existing)
