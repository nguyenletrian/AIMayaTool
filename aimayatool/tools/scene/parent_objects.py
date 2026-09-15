from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def parent_objects(objects, parent=None, world=False):
    """Parent explicit existing objects deterministically, or unparent them to world."""
    cmds = _cmds()
    if world and parent:
        raise ValueError("Specify either parent or world, not both.")
    if not world and (not parent or not cmds.objExists(parent)):
        raise ValueError("Parent does not exist: {0}".format(parent))
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing"})
            continue
        if not world and obj == parent:
            results.append({"object": obj, "status": "skipped_self_parent"})
            continue
        try:
            value = cmds.parent(obj, world=True)[0] if world else cmds.parent(obj, parent)[0]
        except RuntimeError as exc:
            results.append({"object": obj, "status": "skipped_invalid_parent", "error": str(exc)})
            continue
        results.append({"object": obj, "status": "parented", "result": value, "parent": None if world else parent})
    return tuple(results)
