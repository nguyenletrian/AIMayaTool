"""ScenePattern Create Offset composition over the shared Setup zero-group primitive."""

from __future__ import absolute_import


def normalize_create_offset_item(item):
    """Normalize one legacy-compatible CreateOffset item without requiring Maya."""
    if not isinstance(item, dict):
        raise TypeError("CreateOffset item must be a dictionary")
    objects = item.get("objects", [])
    if isinstance(objects, str):
        objects = objects.splitlines()
    objects = tuple(str(node).strip() for node in (objects or ()) if str(node).strip())
    suffix = str(item.get("extraName") or item.get("suffix") or "_ZERO").strip() or "_ZERO"
    return {"objects": objects, "suffix": suffix}


def build_create_offset_plan(items):
    """Build deterministic per-object operations from serialized item data."""
    if items is None:
        return tuple()
    if not isinstance(items, (list, tuple)):
        raise TypeError("CreateOffset items must be a list or tuple")
    plan = []
    for item in items:
        normalized = normalize_create_offset_item(item)
        plan.extend({"object": node, "suffix": normalized["suffix"]} for node in normalized["objects"])
    return tuple(plan)


def execute_create_offset_plan(plan, create_zero_group_fn=None, exists_fn=None):
    """Execute a plan while delegating offset mechanics to Setup."""
    if create_zero_group_fn is None or exists_fn is None:
        import maya.cmds as cmds
        if create_zero_group_fn is None:
            from aimayatool.tools.setup.controls import create_zero_group
            create_zero_group_fn = create_zero_group
        if exists_fn is None:
            exists_fn = cmds.objExists
    results = []
    for entry in tuple(plan or ()):
        node, suffix = entry["object"], entry["suffix"]
        if not node or not exists_fn(node):
            results.append({"object": node, "status": "skipped_missing"})
            continue
        group, child = create_zero_group_fn(node, suffix=suffix)
        results.append({"object": node, "status": "applied", "group": group, "child": child, "suffix": suffix})
    return tuple(results)


def create_offsets(items, create_zero_group_fn=None, exists_fn=None):
    return execute_create_offset_plan(build_create_offset_plan(items), create_zero_group_fn=create_zero_group_fn, exists_fn=exists_fn)


def apply_create_offset(objects, extra_name="_ZERO"):
    """Compatibility convenience wrapper for explicit objects + legacy extraName semantics."""
    return create_offsets([{"objects": tuple(objects or ()), "extraName": extra_name}])
