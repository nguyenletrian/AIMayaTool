from __future__ import absolute_import

import importlib
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import skin_io


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def run_skin_io_undo_smoke():
    importlib.invalidate_caches()
    importlib.reload(skin_io)
    cmds.file(new=True, force=True)
    root = tempfile.mkdtemp(prefix='aimayatool_skin_io_undo_')
    try:
        joint_a = cmds.joint(name='AIMayaToolSkinIOUndoJointA', position=(-1, 0, 0)); cmds.select(clear=True)
        joint_b = cmds.joint(name='AIMayaToolSkinIOUndoJointB', position=(1, 0, 0)); cmds.select(clear=True)
        mesh_a = cmds.polyPlane(name='AIMayaToolSkinIOUndoMeshA', subdivisionsX=1, subdivisionsY=1)[0]
        mesh_b = cmds.polyPlane(name='AIMayaToolSkinIOUndoMeshB', subdivisionsX=1, subdivisionsY=1)[0]
        skin_a = cmds.skinCluster([joint_a, joint_b], mesh_a, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOUndoSkinA')[0]
        skin_b = cmds.skinCluster([joint_a, joint_b], mesh_b, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOUndoSkinB')[0]

        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.8), (joint_b, 0.2)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.3), (joint_b, 0.7)], normalize=True)
        export_report = skin_io.export_meshes([mesh_a, mesh_b], root)
        if export_report['failed']:
            raise RuntimeError('skin IO export failed: %s' % export_report['failed'])

        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.9), (joint_b, 0.1)], normalize=True)
        before_a = _weight(skin_a, mesh_a + '.vtx[0]', joint_a)
        before_b = _weight(skin_b, mesh_b + '.vtx[0]', joint_a)

        report = skin_io.import_meshes_undoable([mesh_a, mesh_b], root, preserve_existing=True, require_existing=True)
        if report['failed']:
            raise RuntimeError('skin IO import failed: %s' % report['failed'])
        if abs(_weight(skin_a, mesh_a + '.vtx[0]', joint_a) - 0.8) > 1e-5:
            raise RuntimeError('mesh A import did not restore exported weights')
        if abs(_weight(skin_b, mesh_b + '.vtx[0]', joint_a) - 0.3) > 1e-5:
            raise RuntimeError('mesh B import did not restore exported weights')

        cmds.undo()
        if abs(_weight(skin_a, mesh_a + '.vtx[0]', joint_a) - before_a) > 1e-5:
            raise RuntimeError('single undo did not restore mesh A pre-import weights')
        if abs(_weight(skin_b, mesh_b + '.vtx[0]', joint_a) - before_b) > 1e-5:
            raise RuntimeError('single undo did not restore mesh B pre-import weights')

        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_IO_IMPORT_UNDO_OK targets=2'
    finally:
        shutil.rmtree(root, ignore_errors=True)
