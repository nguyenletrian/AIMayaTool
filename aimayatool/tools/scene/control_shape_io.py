from __future__ import absolute_import

import json


def _cmds():
    import maya.cmds as cmds
    return cmds


def collect_control_shape_data(controls):
    """Collect deterministic local CV/color/visibility data for explicit curve controls."""
    cmds = _cmds()
    data = {}
    for control in tuple(controls or ()):
        if not control or not cmds.objExists(control):
            continue
        shapes = cmds.listRelatives(control, shapes=True, noIntermediate=True, fullPath=True, type="nurbsCurve") or []
        if not shapes:
            continue
        control_data = {"overrideEnabled": cmds.getAttr(control + ".overrideEnabled"), "overrideRGBColors": cmds.getAttr(control + ".overrideRGBColors"), "visibility": cmds.getAttr(control + ".visibility"), "shapes": []}
        if control_data["overrideRGBColors"]:
            control_data["overrideColorRGB"] = list(cmds.getAttr(control + ".overrideColorRGB")[0])
        else:
            control_data["overrideColor"] = cmds.getAttr(control + ".overrideColor")
        for shape in shapes:
            shape_data = {"name": shape.split("|")[-1], "visibility": cmds.getAttr(shape + ".visibility"), "overrideEnabled": cmds.getAttr(shape + ".overrideEnabled"), "overrideRGBColors": cmds.getAttr(shape + ".overrideRGBColors"), "points": [list(cmds.xform(cv, query=True, objectSpace=True, translation=True)) for cv in cmds.ls(shape + ".cv[*]", flatten=True)]}
            if shape_data["overrideRGBColors"]:
                shape_data["overrideColorRGB"] = list(cmds.getAttr(shape + ".overrideColorRGB")[0])
            else:
                shape_data["overrideColor"] = cmds.getAttr(shape + ".overrideColor")
            control_data["shapes"].append(shape_data)
        data[control] = control_data
    return data


def write_control_shape_json(path, controls):
    data = collect_control_shape_data(controls)
    with open(path, "w") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
    return data


def read_control_shape_json(path):
    with open(path, "r") as stream:
        return json.load(stream)


def apply_control_shape_data(data, controls=None):
    """Apply stored CV/color/visibility data to existing matching controls/shapes."""
    cmds = _cmds()
    allowed = set(controls) if controls is not None else None
    results = []
    for control, control_data in sorted((data or {}).items()):
        if allowed is not None and control not in allowed:
            continue
        if not cmds.objExists(control):
            results.append({"control": control, "status": "skipped_missing"}); continue
        shapes = cmds.listRelatives(control, shapes=True, noIntermediate=True, fullPath=True, type="nurbsCurve") or []
        stored = control_data.get("shapes") or []
        if len(shapes) != len(stored):
            results.append({"control": control, "status": "skipped_shape_mismatch"}); continue
        cmds.setAttr(control + ".overrideEnabled", control_data.get("overrideEnabled", 0)); cmds.setAttr(control + ".overrideRGBColors", control_data.get("overrideRGBColors", 0)); cmds.setAttr(control + ".visibility", control_data.get("visibility", 1))
        if control_data.get("overrideRGBColors") and "overrideColorRGB" in control_data: cmds.setAttr(control + ".overrideColorRGB", *control_data["overrideColorRGB"])
        elif "overrideColor" in control_data: cmds.setAttr(control + ".overrideColor", control_data["overrideColor"])
        mismatch = False
        for shape, shape_data in zip(shapes, stored):
            cvs = cmds.ls(shape + ".cv[*]", flatten=True)
            points = shape_data.get("points") or []
            if len(cvs) != len(points): mismatch = True; break
            for cv, point in zip(cvs, points): cmds.xform(cv, objectSpace=True, translation=point)
            cmds.setAttr(shape + ".visibility", shape_data.get("visibility", 1)); cmds.setAttr(shape + ".overrideEnabled", shape_data.get("overrideEnabled", 0)); cmds.setAttr(shape + ".overrideRGBColors", shape_data.get("overrideRGBColors", 0))
            if shape_data.get("overrideRGBColors") and "overrideColorRGB" in shape_data: cmds.setAttr(shape + ".overrideColorRGB", *shape_data["overrideColorRGB"])
            elif "overrideColor" in shape_data: cmds.setAttr(shape + ".overrideColor", shape_data["overrideColor"])
        results.append({"control": control, "status": "skipped_cv_mismatch" if mismatch else "applied"})
    return tuple(results)
