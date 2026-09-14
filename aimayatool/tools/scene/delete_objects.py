from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def delete_objects(objects):
    """Delete explicit scene objects, skipping missing entries deterministically."""
    cmds = _cmds()
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing"})
            continue
        cmds.delete(obj)
        results.append({"object": obj, "status": "deleted"})
    return tuple(results)
