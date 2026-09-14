from __future__ import absolute_import

import os
import tempfile


def run_scene_animation_backup_smoke():
    import maya.cmds as cmds
    from .animation_backup import write_animation_backup, import_animation_backup

    cmds.file(new=True, force=True)
    node = cmds.createNode("transform", name="AnimBackup_CTRL")
    cmds.setKeyframe(node + ".tx", time=1, value=2.5)
    cmds.setKeyframe(node + ".tx", time=8, value=-3.0)

    path = os.path.join(tempfile.gettempdir(), "aimayatool_scene_animation_backup_smoke.json")
    try:
        data = write_animation_backup(path, [node, "Missing_CTRL"])
        tx = data.get(node, {}).get("tx", {})
        if tx.get("times") != [1.0, 8.0] or tx.get("values") != [2.5, -3.0]:
            raise AssertionError("Animation backup export did not preserve tx keys.")

        cmds.cutKey(node + ".tx", clear=True)
        cmds.setKeyframe(node + ".tx", time=3, value=99.0)
        result = import_animation_backup(path)
        if result != ({"object": node, "status": "applied", "attributes": ("tx",)},):
            raise AssertionError("Animation backup import result was unexpected: {0}".format(result))

        times = cmds.keyframe(node + ".tx", query=True, timeChange=True) or []
        values = cmds.keyframe(node + ".tx", query=True, valueChange=True) or []
        if list(times) != [1.0, 8.0] or list(values) != [2.5, -3.0]:
            raise AssertionError("Animation backup import did not restore tx keys.")
    finally:
        if os.path.exists(path):
            os.remove(path)

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_ANIMATION_BACKUP_OK:1"
