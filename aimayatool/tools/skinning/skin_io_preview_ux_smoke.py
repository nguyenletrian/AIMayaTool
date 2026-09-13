from __future__ import absolute_import

import importlib
import os
import shutil
import tempfile

import maya.cmds as cmds

import aimayatool
import aimayatool.tools.skinning as skinning_ui
from aimayatool.maya import skin
from aimayatool.tools.skinning import skin_io


def run_skin_io_preview_ux_smoke():
    importlib.invalidate_caches()
    importlib.reload(skin_io)
    importlib.reload(skinning_ui)
    cmds.file(new=True, force=True)

    root = tempfile.mkdtemp(prefix='aimayatool_skin_io_preview_ux_')
    try:
        joint_a = cmds.joint(name='AIMayaToolSkinIOPreviewJointA', position=(-1, 0, 0)); cmds.select(clear=True)
        joint_b = cmds.joint(name='AIMayaToolSkinIOPreviewJointB', position=(1, 0, 0)); cmds.select(clear=True)
        mesh_a = cmds.polyPlane(name='AIMayaToolSkinIOPreviewMeshA', subdivisionsX=1, subdivisionsY=1)[0]
        mesh_b = cmds.polyPlane(name='AIMayaToolSkinIOPreviewMeshB', subdivisionsX=1, subdivisionsY=1)[0]
        skin_a = cmds.skinCluster([joint_a, joint_b], mesh_a, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOPreviewSkinA')[0]
        skin_b = cmds.skinCluster([joint_a, joint_b], mesh_b, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOPreviewSkinB')[0]

        cmds.select([mesh_a, mesh_b], replace=True)
        export_preview = skin_io.preview_export_selected(root)
        if len(export_preview) != 3 or not export_preview[0].startswith('Export 2 mesh(es):'):
            raise RuntimeError('unexpected export preview: %s' % export_preview)
        if os.listdir(root):
            raise RuntimeError('export preview mutated filesystem: %s' % os.listdir(root))

        export_report = skin_io.export_meshes([mesh_a, mesh_b], root)
        if export_report['failed']:
            raise RuntimeError('fixture export failed: %s' % export_report['failed'])

        before_a = skin.find_skin_cluster(mesh_a)
        before_b = skin.find_skin_cluster(mesh_b)
        import_preview = skin_io.preview_import_selected(root)
        if len(import_preview) != 3 or not import_preview[0].startswith('Import 2 mesh(es):'):
            raise RuntimeError('unexpected import preview: %s' % import_preview)
        if 'reuse skinCluster' not in import_preview[1] or 'reuse skinCluster' not in import_preview[2]:
            raise RuntimeError('import preview did not explain reuse behavior: %s' % import_preview)
        if skin.find_skin_cluster(mesh_a) != before_a or skin.find_skin_cluster(mesh_b) != before_b:
            raise RuntimeError('import preview mutated skinClusters')
        if before_a != skin_a or before_b != skin_b:
            raise RuntimeError('fixture skinClusters changed unexpectedly')

        aimayatool.launch()
        labels = []
        for control in cmds.lsUI(type='button') or []:
            try:
                labels.append(cmds.button(control, query=True, label=True))
            except Exception:
                pass
        if 'Preview Skin Export' not in labels or 'Preview Skin Import' not in labels:
            raise RuntimeError('Skin IO preview controls not found')

        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_UX_SKIN_IO_PREVIEW_OK targets=2'
    finally:
        shutil.rmtree(root, ignore_errors=True)
