from __future__ import absolute_import

from aimayatool.tools.setup import controls


def apply_clear_offset(objects, suffix="_ClearOffsetGrp"):
    """Insert matched offset groups above explicit objects; missing objects are skipped."""
    cmds = controls._cmds()
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing_object"})
            continue
        group, child_path = controls.create_zero_group(obj, suffix=suffix)
        results.append({
            "object": obj,
            "status": "applied",
            "group": group,
            "child_path": child_path,
        })
    return tuple(results)
