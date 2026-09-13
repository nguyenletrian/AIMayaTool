from __future__ import absolute_import

import importlib
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import skin_io


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def run_skin_io_transaction_smoke():
    importlib.invalidate_caches()
    importlib.reload(skin_io)
    cmds.file(new=True, force=True)
    root = tempfile.mkdtemp(prefix='aimayatool_skin_io_transaction_')
    original_import_skin = skin_io.import_skin
    try:
        joint_a = cmds.joint(name='AIMayaToolSkinIOTransactionJointA', position=(-1, 0, 0)); cmds.select(clear=True)
        joint_b = cmds.joint(name='AIMayaToolSkinIOTransactionJointB', position=(1, 0, 0)); cmds.select(clear=True)
        meshes = [cmds.polyPlane(name='AIMayaToolSkinIOTransactionMesh%s' % suffix, subdivisionsX=1, subdivisionsY=1)[0] for suffix in ('A', 'B', 'C')]
        skins = [cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOTransactionSkin%s' % suffix)[0] for mesh, suffix in zip(meshes, ('A', 'B', 'C'))]

        target_weights = (0.8, 0.6, 0.4)
        for mesh, skin_cluster, value in zip(meshes, skins, target_weights):
            cmds.skinPercent(skin_cluster, mesh + '.vtx[*]', transformValue=[(joint_a, value), (joint_b, 1.0 - value)], normalize=True)
        export_report = skin_io.export_meshes(meshes, root)
        if export_report['failed']:
            raise RuntimeError('target export failed: %s' % export_report['failed'])

        cmds.skinPercent(skins[0], meshes[0] + '.vtx[*]', transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        cmds.skinPercent(skins[2], meshes[2] + '.vtx[*]', transformValue=[(joint_a, 0.9), (joint_b, 0.1)], normalize=True)
        before_a = _weight(skins[0], meshes[0] + '.vtx[0]', joint_a)
        before_c = _weight(skins[2], meshes[2] + '.vtx[0]', joint_a)
        cmds.delete(skins[1])
        if skin.find_skin_cluster(meshes[1]):
            raise RuntimeError('mesh B setup should have no skinCluster')

        def failing_import(mesh, directory, preserve_existing=True, require_existing=False):
            if skin.mesh_from_component(mesh) == skin.mesh_from_component(meshes[2]):
                raise RuntimeError('intentional transaction failure on mesh C')
            return original_import_skin(mesh, directory, preserve_existing=preserve_existing, require_existing=require_existing)

        skin_io.import_skin = failing_import
        report = skin_io.import_meshes_transactional(meshes, root, preserve_existing=True, require_existing=False)
        if not report['failed'] or meshes[2] not in report['failed']:
            raise RuntimeError('transaction did not report mesh C failure: %s' % report)
        if not report['rolled_back'] or report['rollback_failed']:
            raise RuntimeError('transaction rollback was not clean: %s' % report)
        if abs(_weight(skins[0], meshes[0] + '.vtx[0]', joint_a) - before_a) > 1e-5:
            raise RuntimeError('rollback did not restore mesh A weights')
        if abs(_weight(skins[2], meshes[2] + '.vtx[0]', joint_a) - before_c) > 1e-5:
            raise RuntimeError('rollback changed untouched mesh C weights')
        if skin.find_skin_cluster(meshes[1]):
            raise RuntimeError('rollback did not delete newly-created mesh B skinCluster')

        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_IO_TRANSACTION_ROLLBACK_OK targets=3 failed=1'
    finally:
        skin_io.import_skin = original_import_skin
        shutil.rmtree(root, ignore_errors=True)
