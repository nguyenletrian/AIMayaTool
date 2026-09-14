from __future__ import absolute_import

from aimayatool.tools.scene.create_ref import create_references


def _cmds():
    import maya.cmds as cmds
    return cmds


def run_scene_create_ref_smoke():
    cmds = _cmds()
    parent = cmds.group(empty=True, name="RefParent_GRP")
    source = cmds.group(empty=True, name="RefSource_CTRL")
    cmds.xform(source, worldSpace=True, translation=(3.0, 4.0, 5.0), rotation=(10.0, 20.0, 30.0))
    results = create_references((source, "Missing_CTRL"), parent=parent)
    assert results[0]["status"] == "created"
    assert results[1]["status"] == "skipped_missing"
    ref = results[0]["reference"]
    assert ref.endswith("_Ref")
    assert (cmds.listRelatives(ref, parent=True) or [None])[0] == parent
    src_matrix = cmds.xform(source, query=True, worldSpace=True, matrix=True)
    ref_matrix = cmds.xform(ref, query=True, worldSpace=True, matrix=True)
    assert all(abs(a - b) < 1e-5 for a, b in zip(src_matrix, ref_matrix))
    again = create_references((source,), parent=parent)
    assert again[0]["status"] == "skipped_existing"
    try:
        create_references((source,), parent="MissingParent_GRP")
    except ValueError:
        pass
    else:
        raise AssertionError("Missing parent must raise ValueError")
    return "AIBRIDGE_UI_SMOKE_OK:SCENE_CREATE_REF_OK:2"
