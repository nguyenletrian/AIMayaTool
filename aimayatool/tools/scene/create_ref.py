from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def create_references(objects, parent=None, suffix="_Ref"):
    """Create matched reference transforms for existing objects."""
    cmds = _cmds()
    if parent and not cmds.objExists(parent):
        raise ValueError("Parent does not exist: {0}".format(parent))
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing"})
            continue
        name = obj.split("|")[-1] + suffix
        if cmds.objExists(name):
            results.append({"object": obj, "status": "skipped_existing", "reference": name})
            continue
        ref = cmds.group(empty=True, name=name)
        cmds.matchTransform(ref, obj)
        if parent:
            ref = cmds.parent(ref, parent)[0]
        results.append({"object": obj, "status": "created", "reference": ref})
    return tuple(results)
