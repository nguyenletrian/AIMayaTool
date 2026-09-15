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
    extra_name = str(item.get("extraName") or item.get("suffix") or "").strip()
    return {"objects": objects, "extra_name": extra_name}


def build_create_offset_plan(items):
    """Build deterministic per-object operations with the exact legacy group name."""
    if items is None:
        return tuple()
    if not isinstance(items, (list, tuple)):
        raise TypeError("CreateOffset items must be a list or tuple")
    plan = []
    for item in items:
        normalized = normalize_create_offset_item(item)
        for node in normalized["objects"]:
            extra_name = normalized["extra_name"]
            plan.append({"object": node, "group_name": node + extra_name if extra_name else node + "ExtraName"})
    return tuple(plan)


def execute_create_offset_plan(plan, create_offset_group_fn=None, exists_fn=None):
    """Execute a plan while delegating offset-group mechanics to Setup/injected runtime."""
    if create_offset_group_fn is None or exists_fn is None:
        import maya.cmds as cmds
        if create_offset_group_fn is None:
            from aimayatool.tools.setup.controls import create_zero_group
            create_offset_group_fn = lambda node, group_name: create_zero_group(node, suffix=group_name[len(node):])
        if exists_fn is None:
            exists_fn = cmds.objExists
    results = []
    for entry in tuple(plan or ()):
        node, group_name = entry["object"], entry["group_name"]
        if not node or not exists_fn(node):
            results.append({"object": node, "status": "skipped_missing"}); continue
        group, child = create_offset_group_fn(node, group_name)
        results.append({"object": node, "status": "applied", "group": group, "child": child, "group_name": group_name})
    return tuple(results)


def create_offsets(items, create_offset_group_fn=None, exists_fn=None):
    return execute_create_offset_plan(build_create_offset_plan(items), create_offset_group_fn=create_offset_group_fn, exists_fn=exists_fn)


def apply_create_offset(objects, extra_name=""):
    return create_offsets([{"objects": tuple(objects or ()), "extraName": extra_name}])
