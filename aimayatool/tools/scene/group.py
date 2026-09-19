from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def create_groups(items):
    """Create legacy ScenePattern empty groups matched and parented to requested parents."""
    cmds = _cmds()
    results = []
    for item in tuple(items or ()):
        name = str(item.get("name", "")).strip() if isinstance(item, dict) else ""
        parent = str(item.get("parent", "")).strip() if isinstance(item, dict) else ""
        if not name:
            raise ValueError("group name is required")
        if not parent or not cmds.objExists(parent):
            raise ValueError("Parent does not exist: {0}".format(parent))
        grp = cmds.group(empty=True, name=name)
        cmds.matchTransform(grp, parent)
        cmds.parent(grp, parent)
        results.append(grp)
    return tuple(results)


def group_managed_maya_smoke():
    cmds = _cmds()
    cmds.file(new=True, force=True)
    parent = cmds.createNode("transform", name="GroupParent")
    cmds.setAttr(parent + ".translate", 3.0, 4.0, 5.0, type="double3")
    cmds.setAttr(parent + ".rotate", 10.0, 20.0, 30.0, type="double3")
    grp = create_groups(({"name": "LegacyEmptyGroup", "parent": parent},))[0]
    parent_ok = (cmds.listRelatives(grp, parent=True) or [None])[0] == parent
    local_zero = all(abs(v) < 1e-6 for v in (cmds.getAttr(grp + ".translate")[0] + cmds.getAttr(grp + ".rotate")[0]))
    invalid = False
    try: create_groups(({"name": "BadGroup", "parent": "MissingParent"},))
    except ValueError: invalid = True
    success = bool(cmds.objExists(grp) and parent_ok and local_zero and invalid)
    return "AIBRIDGE_UI_SMOKE_OK:{0}".format({"created": cmds.objExists(grp), "parented": parent_ok, "matched": local_zero, "invalid_parent": invalid, "success": success})
