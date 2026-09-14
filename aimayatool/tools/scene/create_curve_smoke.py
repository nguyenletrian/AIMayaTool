"""Maya smoke for ScenePattern create curve parity."""


def run_scene_create_curve_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.create_curve import create_curve, create_curves

    cmds.file(new=True, force=True)
    parent = cmds.group(empty=True, name="CurveParent_GRP")
    result = create_curve(
        points=((0, 0, 0), (1, 2, 0), (3, 2, 1), (5, 0, 0)),
        curve_name="Guide_CRV",
        parent=parent,
        rebuild_spans=8,
    )
    curve = result["curve"]
    rebuilt = result["rebuilt_curve"]
    if result["degree"] != 3 or result["point_count"] != 4 or result["rebuild_spans"] != 8:
        raise AssertionError("Create Curve metadata mismatch.")
    if not cmds.objExists(curve) or not cmds.objExists(rebuilt):
        raise AssertionError("Create Curve did not create source and rebuilt curves.")
    if cmds.getAttr(curve + ".visibility") != 0 or cmds.getAttr(rebuilt + ".visibility") != 0:
        raise AssertionError("Create Curve visibility parity failed.")
    if (cmds.listRelatives(curve, parent=True) or [None])[0] != parent:
        raise AssertionError("Create Curve parent was not preserved.")
    if (cmds.listRelatives(rebuilt, parent=True) or [None])[0] != parent:
        raise AssertionError("Rebuilt curve parent was not preserved.")

    batch = create_curves([
        {"curveName": "Linear_CRV", "points": "0 0 0\n1 0 0", "rebuild": 0},
        {"curveName": "Bad_CRV", "points": "0 0 0", "rebuild": 0},
    ])
    if batch[0]["degree"] != 1 or batch[0]["rebuilt_curve"] is not None:
        raise AssertionError("Create Curve linear/no-rebuild behavior failed.")
    if batch[1].get("status") != "skipped":
        raise AssertionError("Create Curve invalid point data was not skipped deterministically.")

    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CREATE_CURVE_OK:2"
    print(marker)
    return marker
