from __future__ import absolute_import

import os
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import skin_io


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def run_skin_io_batch_smoke():
    cmds.file(new=True, force=True)
    root = tempfile.mkdtemp(prefix='aimayatool_skin_io_')
    progress = []
    try:
        joint_a = cmds.joint(name='AIMayaToolSkinIOJointA', position=(-1, 0, 0)); cmds.select(clear=True)
        joint_b = cmds.joint(name='AIMayaToolSkinIOJointB', position=(1, 0, 0)); cmds.select(clear=True)
        mesh_a = cmds.polyPlane(name='AIMayaToolSkinIOMeshA', subdivisionsX=1, subdivisionsY=1)[0]
        mesh_b = cmds.polyPlane(name='AIMayaToolSkinIOMeshB', subdivisionsX=1, subdivisionsY=1)[0]
        skin_a = cmds.skinCluster([joint_a, joint_b], mesh_a, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOSkinA')[0]
        skin_b = cmds.skinCluster([joint_a, joint_b], mesh_b, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOSkinB')[0]
        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.8), (joint_b, 0.2)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.3), (joint_b, 0.7)], normalize=True)

        before = (skin.find_skin_cluster(mesh_a), skin.find_skin_cluster(mesh_b), sorted(os.listdir(root)))
        export_plan = skin_io.preview_export_meshes([mesh_a, mesh_b], root)
        after_preview = (skin.find_skin_cluster(mesh_a), skin.find_skin_cluster(mesh_b), sorted(os.listdir(root)))
        if before != after_preview or export_plan['count'] != 2:
            raise RuntimeError('export preview mutated state or returned wrong count')

        skin_io.export_meshes([mesh_a, mesh_b], root, progress=lambda i, total, mesh, ok: progress.append(('export', i, total, ok)))
        if len(progress) != 2 or progress[-1][1:3] != (2, 2) or not all(item[3] for item in progress):
            raise RuntimeError('export progress mismatch: %s' % (progress,))

        cmds.skinPercent(skin_a, mesh_a + '.vtx[*]', transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        cmds.skinPercent(skin_b, mesh_b + '.vtx[*]', transformValue=[(joint_a, 0.9), (joint_b, 0.1)], normalize=True)

        before_import = (_weight(skin_a, mesh_a + '.vtx[0]', joint_a), _weight(skin_b, mesh_b + '.vtx[0]', joint_a))
        import_plan = skin_io.preview_import_meshes([mesh_a, mesh_b], root, require_existing=True)
        after_import_preview = (_weight(skin_a, mesh_a + '.vtx[0]', joint_a), _weight(skin_b, mesh_b + '.vtx[0]', joint_a))
        if before_import != after_import_preview or import_plan['count'] != 2:
            raise RuntimeError('import preview mutated weights or returned wrong count')

        progress[:] = []
        report = skin_io.import_meshes([mesh_a, mesh_b], root, preserve_existing=True, require_existing=True, progress=lambda i, total, mesh, ok: progress.append(('import', i, total, ok)))
        if report['failed'] or len(progress) != 2 or progress[-1][1:3] != (2, 2) or not all(item[3] for item in progress):
            raise RuntimeError('import batch/progress mismatch: %s %s' % (report, progress))
        if abs(_weight(skin_a, mesh_a + '.vtx[0]', joint_a) - 0.8) > 1e-5:
            raise RuntimeError('mesh A weights not restored')
        if abs(_weight(skin_b, mesh_b + '.vtx[0]', joint_a) - 0.3) > 1e-5:
            raise RuntimeError('mesh B weights not restored')

        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_IO_BATCH_PREVIEW_OK targets=2 progress=2'
    finally:
        shutil.rmtree(root, ignore_errors=True)
