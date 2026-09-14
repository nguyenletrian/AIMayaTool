"""ScenePattern Create Offset migration using the shared zero-group primitive."""

from aimayatool.tools.setup.controls import create_zero_group


def _cmds():
    import maya.cmds as cmds
    return cmds


def apply_create_offset(objects, extra_name="ExtraName"):
    """Insert a matched offset group above each existing object using a custom suffix."""
    cmds = _cmds()
    suffix = extra_name if extra_name else "ExtraName"
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing"})
            continue
        group, child = create_zero_group(obj, suffix=suffix)
        results.append({"object": obj, "status": "applied", "group": group, "child": child})
    return tuple(results)
