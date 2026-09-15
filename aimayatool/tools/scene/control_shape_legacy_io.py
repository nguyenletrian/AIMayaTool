from __future__ import absolute_import

import json

from aimayatool.tools.scene.control_shape_io import apply_control_shape_data


def convert_legacy_control_shape_data(data):
    """Convert legacy dataCurveShape.json payloads to the deterministic Scene shape schema."""
    converted = {}
    for control, legacy in sorted((data or {}).items()):
        item = {
            "overrideEnabled": legacy.get("overrideEnabled", 0),
            "overrideRGBColors": legacy.get("overrideRGBColors", 0),
            "visibility": legacy.get("visibility", 1),
            "shapes": [],
        }
        if item["overrideRGBColors"]:
            item["overrideColorRGB"] = [legacy.get("overrideColorR", 0.0), legacy.get("overrideColorG", 0.0), legacy.get("overrideColorB", 0.0)]
        elif "overrideColor" in legacy:
            item["overrideColor"] = legacy["overrideColor"]
        for shape_name, shape in sorted((legacy.get("curveData") or {}).items()):
            shape_item = {
                "name": shape_name,
                "visibility": shape.get("visibility", 1),
                "overrideEnabled": shape.get("overrideEnabled", 0),
                "overrideRGBColors": shape.get("overrideRGBColors", 0),
                "points": [list(value) for key, value in sorted((shape.get("pointData") or {}).items(), key=lambda pair: _point_index(pair[0]))],
            }
            if shape_item["overrideRGBColors"]:
                shape_item["overrideColorRGB"] = [shape.get("overrideColorR", 0.0), shape.get("overrideColorG", 0.0), shape.get("overrideColorB", 0.0)]
            elif "overrideColor" in shape:
                shape_item["overrideColor"] = shape["overrideColor"]
            item["shapes"].append(shape_item)
        converted[control] = item
    return converted


def _point_index(name):
    try:
        return int(str(name).split("[")[-1].split("]")[0])
    except (TypeError, ValueError):
        return 10 ** 9


def read_legacy_control_shape_json(path):
    with open(path, "r") as stream:
        return convert_legacy_control_shape_data(json.load(stream))


def import_legacy_control_shape_json(path, controls=None):
    return apply_control_shape_data(read_legacy_control_shape_json(path), controls=controls)
