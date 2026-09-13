from __future__ import absolute_import

import os
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import skin_io


def _uuid(node):
    values = cmds.ls(node, uuid=True) or []
    return values[0] if values else None


def _weights(skin_cluster, vertex, joints):
    return [float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=joint) or 0.0) for joint in joints]


def _assert_weights(skin_cluster, vertex, joints, expected, label):
    actual = _weights(skin_cluster, vertex, joints)
    if any(abs(a - b) > 1e-4 for a, b in zip(actual, expected)):
        raise RuntimeError('%s weights mismatch: %s != %s' % (label, actual, expected))


def run_skin_io_parity_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSkinIOMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolSkinIOJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolSkinIOJointB', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOCluster')[0]
    vertex = mesh + '.vtx[0]'
    expected = [0.75, 0.25]
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, expected[0]), (joint_b, expected[1])], normalize=True)
    directory = tempfile.mkdtemp(prefix='aimayatool_skin_io_')
    scene_directory = tempfile.mkdtemp(prefix='aimayatool_skin_io_scene_')
    try:
        weights_path = skin_io.export_skin(mesh, directory)
        if not weights_path or not os.path.isfile(weights_path) or not skin_io._read_manifest(directory):
            raise RuntimeError('skin export did not create weights and manifest')

        batch_report = skin_io.export_meshes([mesh], directory)
        if mesh not in batch_report['succeeded'] or batch_report['failed']:
            raise RuntimeError('batch skin export report failed: %s' % batch_report)

        original_uuid = _uuid(skin_cluster)
        cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        imported_skin = skin_io.import_skin(mesh, directory, preserve_existing=True)
        if _uuid(imported_skin) != original_uuid:
            raise RuntimeError('preserve-existing import replaced the skinCluster')
        _assert_weights(imported_skin, vertex, [joint_a, joint_b], expected, 'preserve-existing import')

        cmds.skinPercent(imported_skin, vertex, transformValue=[(joint_a, 0.35), (joint_b, 0.65)], normalize=True)
        strict_existing = skin_io.import_existing_skin(mesh, directory)
        if _uuid(strict_existing) != original_uuid:
            raise RuntimeError('strict existing import replaced the skinCluster')
        _assert_weights(strict_existing, vertex, [joint_a, joint_b], expected, 'strict existing import')

        cmds.delete(strict_existing)
        try:
            skin_io.import_existing_skin(mesh, directory)
        except RuntimeError as exc:
            if 'Existing skinCluster required' not in str(exc):
                raise
        else:
            raise RuntimeError('strict existing import created a missing skinCluster')

        rebuilt_skin = skin_io.import_skin(mesh, directory, preserve_existing=True)
        if not rebuilt_skin or skin.find_skin_cluster(mesh) != rebuilt_skin:
            raise RuntimeError('normal import did not recreate the missing skinCluster')
        _assert_weights(rebuilt_skin, vertex, [joint_a, joint_b], expected, 'normal recreate import')

        rebuilt_uuid = _uuid(rebuilt_skin)
        replaced_skin = skin_io.import_skin(mesh, directory, preserve_existing=False)
        replaced_uuid = _uuid(replaced_skin)
        if not replaced_uuid or replaced_uuid == rebuilt_uuid or skin.find_skin_cluster(mesh) != replaced_skin:
            raise RuntimeError('replace-existing import did not rebuild the skinCluster')
        _assert_weights(replaced_skin, vertex, [joint_a, joint_b], expected, 'replace-existing import')

        batch_import = skin_io.import_existing_meshes([mesh], directory)
        if mesh not in batch_import['succeeded'] or batch_import['failed']:
            raise RuntimeError('strict existing batch skin import report failed: %s' % batch_import)

        scene_path = os.path.join(scene_directory, 'SkinIOQuickSmoke.ma')
        cmds.file(rename=scene_path)
        cmds.file(save=True, type='mayaAscii')
        quick_directory = skin_io.quick_directory(create=True)
        expected_quick = os.path.normpath(os.path.join(scene_directory, 'NLTA_Data', 'MeshExport'))
        if quick_directory != expected_quick:
            raise RuntimeError('quick skin directory mismatch: %s != %s' % (quick_directory, expected_quick))
        cmds.select(mesh, replace=True)
        quick_exports = skin_io.export_quick_selected()
        if not quick_exports or not os.path.isfile(quick_exports[0]):
            raise RuntimeError('quick skin export did not create weights')
        cmds.skinPercent(replaced_skin, vertex, transformValue=[(joint_a, 0.2), (joint_b, 0.8)], normalize=True)
        skin_io.import_quick_existing_selected()
        _assert_weights(replaced_skin, vertex, [joint_a, joint_b], expected, 'quick strict existing skin import')
    finally:
        shutil.rmtree(directory, ignore_errors=True)
        shutil.rmtree(scene_directory, ignore_errors=True)
    return 'SKINNING_SKIN_IO_PARITY_SMOKE_OK'
