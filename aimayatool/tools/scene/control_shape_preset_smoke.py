from __future__ import absolute_import


def run_scene_control_shape_preset_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.control_shape_preset import apply_control_shape_preset
    cmds.file(new=True, force=True)
    ctrl = cmds.circle(name="Preset_CTRL", constructionHistory=False)[0]
    matrix = cmds.xform(ctrl, query=True, worldSpace=True, matrix=True)
    result = apply_control_shape_preset((ctrl, "Missing_CTRL"), shape="box", size=2.0)
    assert result[0]["status"] == "applied" and result[0]["preset"] == "box"
    assert result[1]["status"] == "skipped_missing"
    assert cmds.xform(ctrl, query=True, worldSpace=True, matrix=True) == matrix
    shape = (cmds.listRelatives(ctrl, shapes=True, type="nurbsCurve", fullPath=True) or [None])[0]
    assert shape and len(cmds.ls(shape + ".cv[*]", flatten=True) or []) == 16
    invalid = cmds.createNode("transform", name="NoCurve_GRP")
    assert apply_control_shape_preset((invalid,), shape="circle")[0]["status"] == "skipped_invalid_control"
    try:
        apply_control_shape_preset((ctrl,), shape="NotAShape")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported preset must raise ValueError")
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CONTROL_SHAPE_PRESET_OK:2"
    print(marker)
    return marker
