from __future__ import absolute_import


def run_scene_control_shape_io_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.control_shape_io import collect_control_shape_data, apply_control_shape_data
    cmds.file(new=True, force=True)
    ctrl = cmds.circle(name="Shape_CTRL", normal=(1, 0, 0), radius=2, constructionHistory=False)[0]
    shape = cmds.listRelatives(ctrl, shapes=True, fullPath=True)[0]
    cmds.setAttr(ctrl + ".overrideEnabled", 1); cmds.setAttr(ctrl + ".overrideColor", 13)
    data = collect_control_shape_data((ctrl, "Missing_CTRL"))
    assert ctrl in data and len(data[ctrl]["shapes"]) == 1
    original = list(data[ctrl]["shapes"][0]["points"][0])
    first_cv = cmds.ls(shape + ".cv[*]", flatten=True)[0]
    cmds.xform(first_cv, objectSpace=True, translation=(9, 9, 9)); cmds.setAttr(ctrl + ".overrideColor", 6)
    result = apply_control_shape_data(data)
    assert result == ({"control": ctrl, "status": "applied"},)
    restored = cmds.xform(first_cv, query=True, objectSpace=True, translation=True)
    assert all(abs(a - b) < 1e-5 for a, b in zip(restored, original)) and cmds.getAttr(ctrl + ".overrideColor") == 13
    missing_data = {"Missing_CTRL": data[ctrl]}
    assert apply_control_shape_data(missing_data) == ({"control": "Missing_CTRL", "status": "skipped_missing"},)
    mismatch = cmds.circle(name="Mismatch_CTRL", normal=(1, 0, 0), sections=4, constructionHistory=False)[0]
    mismatch_data = {mismatch: data[ctrl]}
    assert apply_control_shape_data(mismatch_data)[0]["status"] in ("skipped_shape_mismatch", "skipped_cv_mismatch")
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CONTROL_SHAPE_IO_OK:1"
    print(marker); return marker
