from __future__ import absolute_import


def run_scene_control_shape_copy_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.control_shape_copy import copy_curve_shape, mirror_curve_shape
    cmds.file(new=True, force=True)
    source = cmds.curve(name="Source_CTRL", degree=1, point=[(1, 0, 0), (2, 1, 0), (3, 0, 0)])
    target = cmds.circle(name="Target_CTRL", normal=(0, 1, 0), constructionHistory=False)[0]
    before_matrix = cmds.xform(target, query=True, worldSpace=True, matrix=True)
    copied = copy_curve_shape(source, (target, "Missing_CTRL"))
    assert copied[0]["status"] == "copied" and copied[1]["status"] == "skipped_missing"
    assert cmds.xform(target, query=True, worldSpace=True, matrix=True) == before_matrix
    assert len(cmds.ls(target + "Shape.cv[*]", flatten=True) or []) == 3
    mirror = cmds.curve(name="Mirror_CTRL", degree=1, point=[(0, 0, 0), (0, 0, 0), (0, 0, 0)])
    result = mirror_curve_shape(source, mirror, axis="x")
    assert result["status"] == "mirrored" and result["cv_count"] == 3
    src = cmds.pointPosition(source + "Shape.cv[1]", world=True); dst = cmds.pointPosition(mirror + "Shape.cv[1]", world=True)
    assert abs(dst[0] + src[0]) < 1e-5 and abs(dst[1] - src[1]) < 1e-5 and abs(dst[2] - src[2]) < 1e-5
    mismatch = cmds.circle(name="Mismatch_CTRL", constructionHistory=False)[0]
    assert mirror_curve_shape(source, mismatch)["status"] == "skipped_cv_mismatch"
    assert mirror_curve_shape("Missing_CTRL", mirror)["status"] == "skipped_missing"
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CONTROL_SHAPE_COPY_OK:3"; print(marker); return marker
