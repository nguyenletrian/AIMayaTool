from __future__ import absolute_import


def normalize_control_shape_item(item):
    """Normalize one ScenePattern control-shape item without touching Maya."""
    if not isinstance(item, dict):
        raise TypeError("ControlShape item must be a dictionary")
    objects = item.get("objects", [])
    if isinstance(objects, str):
        objects = objects.splitlines()
    objects = tuple(str(node).strip() for node in (objects or []) if str(node).strip())
    shape = str(item.get("shape") or item.get("controlShape") or "circle").strip().lower()
    size = float(item.get("size", 1.0))
    if size <= 0.0:
        raise ValueError("ControlShape size must be greater than zero.")
    return {"objects": objects, "shape": shape, "size": size}


def build_control_shape_plan(items):
    """Return deterministic per-control replacement calls."""
    if items is None:
        return []
    if not isinstance(items, (list, tuple)):
        raise TypeError("ControlShape items must be a list or tuple")
    plan = []
    for item in items:
        spec = normalize_control_shape_item(item)
        for node in spec["objects"]:
            plan.append({"object": node, "shape": spec["shape"], "size": spec["size"]})
    return plan


def execute_control_shape_plan(plan, replace_control_shape_fn=None):
    """Execute Scene data by delegating curve-shape mechanics to Setup."""
    if replace_control_shape_fn is None:
        from aimayatool.tools.setup.controls import replace_control_shape
        replace_control_shape_fn = replace_control_shape
    result = []
    for entry in plan:
        transform, shape_node = replace_control_shape_fn(entry["object"], shape=entry["shape"], size=entry["size"])
        result.append({"object": entry["object"], "transform": transform, "shape_node": shape_node})
    return result


def apply_control_shapes(items, replace_control_shape_fn=None):
    return execute_control_shape_plan(build_control_shape_plan(items), replace_control_shape_fn)
