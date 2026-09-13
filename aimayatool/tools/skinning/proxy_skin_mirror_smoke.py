from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import proxy_skin


def _uuids(nodes):
    result = set()
    for node in nodes or []:
        values = cmds.ls(node, uuid=True) or []
        if not values:
            raise RuntimeError('could not resolve node identity: %s' % node)
        result.add(values[0])
    return result


def _weight_total(skin_cluster, component, influences):
    return sum(cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influences)


def _axis_center(mesh, axis):
    index = ('x', 'y', 'z').index(axis)
    bounds = cmds.exactWorldBoundingBox(mesh)
    return (bounds[index] + bounds[index + 3]) * 0.5


def _build_source(axis):
    mesh = cmds.polyCube(name='AIMayaToolProxyMirrorSource_' + axis, width=2.0, height=2.0, depth=2.0)[0]
    cmds.move(2.0 if axis == 'x' else 0.0, 2.0 if axis == 'y' else 0.0, 2.0 if axis == 'z' else 0.0, mesh, absolute=True, worldSpace=True)
    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIMayaToolProxyMirrorJointA_' + axis, position=(-2, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolProxyMirrorJointB_' + axis, position=(2, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], mesh, normalizeWeights=1, name='AIMayaToolProxyMirrorSourceSkin_' + axis)[0]
    vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    for index, vertex in enumerate(vertices):
        value = 1.0 if index % 2 == 0 else 0.25
        cmds.skinPercent(source_skin, vertex, transformValue=[(joint_a, value), (joint_b, 1.0 - value)], normalize=True)
    return mesh, [joint_a, joint_b]


def run_proxy_skin_mirror_smoke():
    cmds.file(new=True, force=True)
    for axis in ('x', 'y', 'z'):
        mesh, joints = _build_source(axis)
        source_faces = cmds.ls(mesh + '.f[*]', flatten=True) or []
        result = proxy_skin.create_mirrored_proxy([source_faces[0]], axis=axis, name='AIMayaToolProxyMirrored_' + axis, copy_skin_weights=True)
        proxy = result['proxy_mesh']
        if result['axis'] != axis:
            raise RuntimeError('proxy mirror axis mismatch: %s' % axis)
        if result['axis_direction'] != 1:
            raise RuntimeError('positive-side axis direction mismatch: %s' % axis)
        if not cmds.objExists(proxy):
            raise RuntimeError('mirrored proxy was not created: %s' % axis)
        if _axis_center(proxy, axis) >= 0.0:
            raise RuntimeError('mirrored proxy did not cross to negative side: %s' % axis)
        target_skin = result['skin_cluster']
        if not target_skin:
            raise RuntimeError('mirrored proxy skinCluster missing: %s' % axis)
        if _uuids(skin.influences(target_skin)) != _uuids(joints):
            raise RuntimeError('mirrored proxy influence identity mismatch: %s' % axis)
        vertices = cmds.ls(proxy + '.vtx[*]', flatten=True) or []
        if not vertices:
            raise RuntimeError('mirrored proxy has no vertices: %s' % axis)
        if any(abs(_weight_total(target_skin, vertex, joints) - 1.0) > 1e-5 for vertex in vertices):
            raise RuntimeError('mirrored proxy weights are not normalized: %s' % axis)
    return 'SKINNING_PROXY_SKIN_AXIS_MIRROR_SMOKE_OK'
