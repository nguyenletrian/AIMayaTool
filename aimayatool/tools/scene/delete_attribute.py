from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def delete_attributes(plugs):
    """Delete explicit existing attribute plugs and deterministically skip missing plugs."""
    cmds = _cmds()
    results = []
    for plug in tuple(plugs or ()):
        if not plug or not cmds.objExists(plug):
            results.append({"plug": plug, "status": "skipped_missing"})
            continue
        try:
            cmds.deleteAttr(plug)
        except RuntimeError as exc:
            results.append({"plug": plug, "status": "skipped_not_deletable", "error": str(exc)})
            continue
        results.append({"plug": plug, "status": "deleted"})
    return tuple(results)
