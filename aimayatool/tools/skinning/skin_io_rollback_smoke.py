from __future__ import absolute_import

import importlib
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.tools.skinning import skin_io


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def run_skin_io_rollback_smoke():
    importlib.invalidate_caches()
    importlib.reload(skin_io)
    cmds.file(new=True, force=True)
    root = tempfile.mkdtemp(prefix='aimayatool_skin_io_rollback_')
    target_dir = root + '/target'
    snapshot_dir = root + '/snapshot'
    try:
        joint_a = cmds.joint(name='AIMayaToolSkinIORollbackJointA', position=(-1, 0, 0)); cmds.select(clear=True)
        joint_b = cmds.joint(name='AIMayaToolSkinIORollbackJointB', position=(1, 0, 0)); cmds.select(clear=True)
        mesh_a = cmds.polyPlane(name='AIMayaToolSkinIORollbackMeshA', subdivisionsX=1, subdivisionsY=1)[0]
        mesh_b = cmds.polyPlane(name='AIMayaToolSkinIORollbackMeshB', subdivisionsX=1, subdivisionsY=1)[0]
        skin_a = cmds.skinCluster([joint_a, joint_b], mesh_a, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIORollbackSkinA')[0]
        skin_b = cmds.skinCluster([joint_a, joint_b], mesh_b, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIORollbackSkinB')[0]

        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.8), (joint_b, 0.2)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.3), (joint_b, 0.7)], normalize=True)
        if skin_io.export_meshes([mesh_a, mesh_b], target_dir)['failed']:
            raise RuntimeError('target export failed')

        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.9), (joint_b, 0.1)], normalize=True)
        before_a = _weight(skin_a, mesh_a + '.vtx[0]', joint_a)
        before_b = _weight(skin_b, mesh_b + '.vtx[0]', joint_a)
        if skin_io.export_meshes([mesh_a, mesh_b], snapshot_dir)['failed']:
            raise RuntimeError('snapshot export failed')

        if skin_io.import_meshes([mesh_a, mesh_b], target_dir, preserve_existing=True, require_existing=True)['failed']:
            raise RuntimeError('target import failed')
        if abs(_weight(skin_a, mesh_a + '.vtx[0]', joint_a) - 0.8) > 1e-5 or abs(_weight(skin_b, mesh_b + '.vtx[0]', joint_a) - 0.3) > 1e-5:
            raise RuntimeError('target import weights incorrect')

        if skin_io.import_meshes([mesh_a, mesh_b], snapshot_dir, preserve_existing=True, require_existing=True)['failed']:
            raise RuntimeError('rollback import failed')
        if abs(_weight(skin_a, mesh_a + '.vtx[0]', joint_a) - before_a) > 1e-5:
            raise RuntimeError('rollback did not restore mesh A')
        if abs(_weight(skin_b, mesh_b + '.vtx[0]', joint_a) - before_b) > 1e-5:
            raise RuntimeError('rollback did not restore mesh B')

        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_IO_EXPLICIT_ROLLBACK_OK targets=2'
    finally:
        shutil.rmtree(root, ignore_errors=True)
