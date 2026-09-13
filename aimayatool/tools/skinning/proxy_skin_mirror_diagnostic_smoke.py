from __future__ import absolute_import

import json
import maya.cmds as cmds

from aimayatool.tools.skinning import proxy_skin


def _bounds(mesh):
    values = cmds.exactWorldBoundingBox(mesh)
    return [round(value, 6) for value in values]


def run_proxy_skin_mirror_diagnostic_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyCube(name='AIMayaToolProxyMirrorDiagSource', width=2.0, height=2.0, depth=2.0)[0]
    cmds.move(2.0, 0.0, 0.0, mesh, absolute=True, worldSpace=True)
    face = (cmds.ls(mesh + '.f[*]', flatten=True) or [])[0]
    source_bounds = _bounds(face)
    direction = proxy_skin._region_axis_direction([face], 'x')
    proxy = proxy_skin.extract_faces([face], name='AIMayaToolProxyMirrorDiag')
    before_bounds = _bounds(proxy)
    before_faces = cmds.polyEvaluate(proxy, face=True)
    cmds.polyMirrorFace(proxy, cutMesh=1, axis=0, axisDirection=direction, mergeMode=0, mergeThresholdType=0)
    after_bounds = _bounds(proxy)
    after_faces = cmds.polyEvaluate(proxy, face=True)
    payload = {
        'axis': 'x',
        'axis_direction': direction,
        'source_face_bounds': source_bounds,
        'proxy_before_bounds': before_bounds,
        'proxy_before_faces': before_faces,
        'proxy_after_bounds': after_bounds,
        'proxy_after_faces': after_faces,
    }
    return 'SKINNING_PROXY_MIRROR_DIAGNOSTIC_OK|' + json.dumps(payload, sort_keys=True)
