from __future__ import absolute_import

import json
import os
import tempfile


def run_scene_control_shape_legacy_io_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.scene.control_shape_legacy_io import import_legacy_control_shape_json
    cmds.file(new=True, force=True)
    control = cmds.curve(name="Legacy_CTRL", degree=1, point=[(0, 0, 0), (1, 1, 0), (2, 0, 0)])
    shape = (cmds.listRelatives(control, shapes=True, noIntermediate=True, type="nurbsCurve") or [None])[0]
    legacy = {control: {"overrideEnabled": 1, "overrideRGBColors": 0, "overrideColor": 13, "visibility": 1, "curveData": {shape: {"overrideEnabled": 1, "overrideRGBColors": 0, "overrideColor": 6, "visibility": 1, "pointData": {"controlPoints[2]": [4, 0, 0], "controlPoints[0]": [2, 0, 0], "controlPoints[1]": [3, 1, 0]}}}}}
    path = os.path.join(tempfile.gettempdir(), "aibridge_legacy_control_shape.json")
    with open(path, "w") as stream:
        json.dump(legacy, stream)
    try:
        results = import_legacy_control_shape_json(path)
        assert results[0]["status"] == "applied"
        assert cmds.getAttr(control + ".overrideColor") == 13 and cmds.getAttr(shape + ".overrideColor") == 6
        points = [cmds.xform(cv, query=True, objectSpace=True, translation=True) for cv in cmds.ls(shape + ".cv[*]", flatten=True)]
        assert points == [[2.0, 0.0, 0.0], [3.0, 1.0, 0.0], [4.0, 0.0, 0.0]]
        assert import_legacy_control_shape_json(path, controls=("Missing_CTRL",)) == ()
    finally:
        if os.path.exists(path): os.remove(path)
    marker = "AIBRIDGE_UI_SMOKE_OK:SCENE_CONTROL_SHAPE_LEGACY_IO_OK:3"; print(marker); return marker
