from __future__ import absolute_import

import os
import shutil
import tempfile

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import copy_weights
from aimayatool.tools.skinning import influences
from aimayatool.tools.skinning import max_influences
from aimayatool.tools.skinning import mirror_skin
from aimayatool.tools.skinning import skin_io
from aimayatool.tools.skinning import utilities


def run_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSkinSmokeMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolSkinSmokeJointA', position=(0, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolSkinSmokeJointB', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster(joint_a, mesh, toSelectedBones=True, name='AIMayaToolSkinSmokeCluster')[0]
    if skin.find_skin_cluster(mesh) != skin_cluster:
        raise RuntimeError('skinCluster discovery failed')
    added = influences.add(mesh, [joint_b])
    if added != [joint_b] or joint_b not in skin.influences(skin_cluster):
        raise RuntimeError('add influence smoke failed')
    removed = influences.remove(mesh, [joint_b])
    if removed != [joint_b] or joint_b in skin.influences(skin_cluster):
        raise RuntimeError('remove influence smoke failed')
    return 'SKINNING_INFLUENCE_SMOKE_OK'


def run_max_influence_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolMaxInfluenceSmokeMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolMaxInfluenceJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolMaxInfluenceJointB', position=(0, 0, 0))
    cmds.select(clear=True)
    joint_c = cmds.joint(name='AIMayaToolMaxInfluenceJointC', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, maximumInfluences=2, normalizeWeights=1, name='AIMayaToolMaxInfluenceSmokeCluster')[0]
    vertex = mesh + '.vtx[0]'
    cmds.setAttr(skin_cluster + '.maintainMaxInfluences', 0)
    if max_influences.configured_limit(skin_cluster) != 2:
        raise RuntimeError('smoke setup max influence limit is not two')
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.5), (joint_b, 0.3), (joint_c, 0.2)], normalize=True)
    before = dict(max_influences._vertex_weights(skin_cluster, vertex))
    nonzero_before = [joint for joint, value in before.items() if abs(value) > 1e-8]
    if len(nonzero_before) != 3:
        raise RuntimeError('smoke setup failed to create three non-zero influences: %s' % before)
    violating = max_influences.violating_vertices(mesh)
    if vertex not in violating:
        raise RuntimeError('max influence validation failed: %s' % before)
    fixed = max_influences.fix(mesh)
    if vertex not in fixed:
        raise RuntimeError('max influence fix did not report target vertex')
    remaining = max_influences.violating_vertices(mesh)
    if remaining:
        raise RuntimeError('max influence fix left violations: %s' % remaining)
    after = dict(max_influences._vertex_weights(skin_cluster, vertex))
    kept = [joint for joint, value in after.items() if abs(value) > 1e-8]
    if set(kept) != set([joint_a, joint_b]):
        raise RuntimeError('max influence fix did not preserve strongest influences: %s' % after)
    if abs(sum(after.values()) - 1.0) > 1e-6:
        raise RuntimeError('max influence fix did not normalize weights: %s' % after)
    return 'SKINNING_MAX_INFLUENCE_SMOKE_OK'


def run_copy_weights_smoke():
    cmds.file(new=True, force=True)
    source = cmds.polyPlane(name='AIMayaToolCopySkinSource', subdivisionsX=1, subdivisionsY=1)[0]
    target = cmds.polyPlane(name='AIMayaToolCopySkinTarget', subdivisionsX=1, subdivisionsY=1)[0]
    cmds.move(0, 0, 2, target)
    joint_a = cmds.joint(name='AIMayaToolCopySkinJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolCopySkinJointB', position=(1, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], source, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolCopySkinSourceCluster')[0]
    source_vertex = source + '.vtx[0]'
    target_vertex = target + '.vtx[0]'
    cmds.skinPercent(source_skin, source_vertex, transformValue=[(joint_a, 0.8), (joint_b, 0.2)], normalize=True)
    target_skin = copy_weights.copy(source, target)
    if skin.find_skin_cluster(target) != target_skin:
        raise RuntimeError('copy weights did not create target skinCluster')
    target_influences = set(skin.influences(target_skin))
    if target_influences != set([joint_a, joint_b]):
        raise RuntimeError('copy weights target influences mismatch: %s' % sorted(target_influences))
    source_values = cmds.skinPercent(source_skin, source_vertex, query=True, value=True) or []
    target_values = cmds.skinPercent(target_skin, target_vertex, query=True, value=True) or []
    if len(source_values) != len(target_values):
        raise RuntimeError('copy weights value count mismatch')
    if any(abs(a - b) > 1e-5 for a, b in zip(source_values, target_values)):
        raise RuntimeError('copy weights mismatch: source=%s target=%s' % (source_values, target_values))
    return 'SKINNING_COPY_WEIGHTS_SMOKE_OK'


def run_mirror_skin_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolMirrorSkinMesh', width=4, height=2, subdivisionsX=2, subdivisionsY=1)[0]
    joint_left = cmds.joint(name='AIMayaToolMirrorSkinJointL', position=(-1.5, 0, 0))
    cmds.select(clear=True)
    joint_right = cmds.joint(name='AIMayaToolMirrorSkinJointR', position=(1.5, 0, 0))
    skin_cluster = cmds.skinCluster([joint_left, joint_right], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolMirrorSkinCluster')[0]
    vertex_count = int(cmds.polyEvaluate(mesh, vertex=True) or 0)
    positions = []
    for index in range(vertex_count):
        vertex = mesh + '.vtx[%d]' % index
        position = cmds.xform(vertex, query=True, worldSpace=True, translation=True) or []
        if len(position) == 3:
            positions.append((vertex, tuple(position)))
    left_candidates = [(vertex, position) for vertex, position in positions if position[0] < -0.5]
    right_candidates = [(vertex, position) for vertex, position in positions if position[0] > 0.5]
    if not left_candidates or not right_candidates:
        raise RuntimeError('mirror smoke could not resolve opposite-side vertices')
    left_vertex, left_position = left_candidates[0]
    right_vertex, right_position = min(right_candidates, key=lambda item: abs(item[1][0] + left_position[0]) + abs(item[1][1] - left_position[1]) + abs(item[1][2] - left_position[2]))
    pair_error = abs(right_position[0] + left_position[0]) + abs(right_position[1] - left_position[1]) + abs(right_position[2] - left_position[2])
    if pair_error > 1e-5:
        raise RuntimeError('mirror smoke could not resolve an exact symmetric vertex pair: left=%s right=%s' % (left_position, right_position))
    source_values = [(joint_left, 0.8), (joint_right, 0.2)]
    destination_values = [(joint_left, 1.0), (joint_right, 0.0)]
    expected_left = 0.2
    expected_right = 0.8
    def _author_fixture():
        cmds.skinPercent(skin_cluster, left_vertex, transformValue=source_values, normalize=True)
        cmds.skinPercent(skin_cluster, right_vertex, transformValue=destination_values, normalize=True)
    def _destination_matches():
        left_weight = cmds.skinPercent(skin_cluster, right_vertex, query=True, transform=joint_left)
        right_weight = cmds.skinPercent(skin_cluster, right_vertex, query=True, transform=joint_right)
        return abs(left_weight - expected_left) <= 1e-4 and abs(right_weight - expected_right) <= 1e-4
    _author_fixture()
    mirror_skin.mirror(mesh, axis='x', inverse=False)
    if not _destination_matches():
        _author_fixture()
        mirror_skin.mirror(mesh, axis='x', inverse=True)
        if not _destination_matches():
            actual_left = cmds.skinPercent(skin_cluster, right_vertex, query=True, transform=joint_left)
            actual_right = cmds.skinPercent(skin_cluster, right_vertex, query=True, transform=joint_right)
            raise RuntimeError('mirror skin destination mismatch: left=%s right=%s expected=(%s, %s)' % (actual_left, actual_right, expected_left, expected_right))
    return 'SKINNING_MIRROR_SKIN_SMOKE_OK'


def run_skin_utilities_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSkinUtilitiesMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolSkinUtilitiesJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolSkinUtilitiesJointB', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinUtilitiesCluster')[0]
    vertex = mesh + '.vtx[0]'
    utilities.lock_all(mesh)
    if any(int(cmds.getAttr(joint + '.liw')) != 1 for joint in (joint_a, joint_b)):
        raise RuntimeError('lock-all utility failed')
    utilities.unlock_all(mesh)
    if any(int(cmds.getAttr(joint + '.liw')) != 0 for joint in (joint_a, joint_b)):
        raise RuntimeError('unlock-all utility failed')
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.99), (joint_b, 0.01)], normalize=True)
    utilities.prune(mesh, threshold=0.05, components=[vertex])
    pruned_b = float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=joint_b) or 0.0)
    if pruned_b > 1e-6:
        raise RuntimeError('prune utility left small weight: %s' % pruned_b)
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.6), (joint_b, 0.4)], normalize=True)
    changed = utilities.clear_influence([vertex], joint_a)
    if changed != [vertex]:
        raise RuntimeError('clear utility did not report target vertex')
    cleared_a = float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=joint_a) or 0.0)
    kept_b = float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=joint_b) or 0.0)
    if cleared_a > 1e-6 or abs(kept_b - 1.0) > 1e-6:
        raise RuntimeError('clear utility failed redistribution: A=%s B=%s' % (cleared_a, kept_b))
    affected = utilities.affected_vertices(mesh, [joint_b], threshold=0.5)
    if vertex not in affected:
        raise RuntimeError('affected-vertices utility did not include weighted vertex')
    if vertex in utilities.affected_vertices(mesh, [joint_a], threshold=0.0001):
        raise RuntimeError('affected-vertices utility included cleared influence')
    return 'SKINNING_UTILITIES_SMOKE_OK'


def run_skin_io_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSkinIOMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolSkinIOJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolSkinIOJointB', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkinIOCluster')[0]
    vertex = mesh + '.vtx[0]'
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.75), (joint_b, 0.25)], normalize=True)
    directory = tempfile.mkdtemp(prefix='aimayatool_skin_io_')
    scene_directory = tempfile.mkdtemp(prefix='aimayatool_skin_io_scene_')
    try:
        weights_path = skin_io.export_skin(mesh, directory)
        if not weights_path or not skin_io._read_manifest(directory):
            raise RuntimeError('skin export did not create weights and manifest')

        batch_report = skin_io.export_meshes([mesh], directory)
        if mesh not in batch_report['succeeded'] or batch_report['failed']:
            raise RuntimeError('batch skin export report failed: %s' % batch_report)

        cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.1), (joint_b, 0.9)], normalize=True)
        imported_skin = skin_io.import_skin(mesh, directory, preserve_existing=True)
        if imported_skin != skin_cluster:
            raise RuntimeError('preserve-existing import replaced the skinCluster')
        restored_a = float(cmds.skinPercent(imported_skin, vertex, query=True, transform=joint_a) or 0.0)
        restored_b = float(cmds.skinPercent(imported_skin, vertex, query=True, transform=joint_b) or 0.0)
        if abs(restored_a - 0.75) > 1e-4 or abs(restored_b - 0.25) > 1e-4:
            raise RuntimeError('skin import did not restore weights: A=%s B=%s' % (restored_a, restored_b))

        replaced_skin = skin_io.import_skin(mesh, directory, preserve_existing=False)
        if replaced_skin == imported_skin or skin.find_skin_cluster(mesh) != replaced_skin:
            raise RuntimeError('replace-existing import did not rebuild the skinCluster')
        replaced_a = float(cmds.skinPercent(replaced_skin, vertex, query=True, transform=joint_a) or 0.0)
        replaced_b = float(cmds.skinPercent(replaced_skin, vertex, query=True, transform=joint_b) or 0.0)
        if abs(replaced_a - 0.75) > 1e-4 or abs(replaced_b - 0.25) > 1e-4:
            raise RuntimeError('replace-existing import did not restore weights: A=%s B=%s' % (replaced_a, replaced_b))

        batch_import = skin_io.import_meshes([mesh], directory, preserve_existing=True)
        if mesh not in batch_import['succeeded'] or batch_import['failed']:
            raise RuntimeError('batch skin import report failed: %s' % batch_import)

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
        skin_io.import_quick_selected(preserve_existing=True)
        quick_a = float(cmds.skinPercent(replaced_skin, vertex, query=True, transform=joint_a) or 0.0)
        quick_b = float(cmds.skinPercent(replaced_skin, vertex, query=True, transform=joint_b) or 0.0)
        if abs(quick_a - 0.75) > 1e-4 or abs(quick_b - 0.25) > 1e-4:
            raise RuntimeError('quick skin import did not restore weights: A=%s B=%s' % (quick_a, quick_b))
    finally:
        shutil.rmtree(directory, ignore_errors=True)
        shutil.rmtree(scene_directory, ignore_errors=True)
    return 'SKINNING_SKIN_IO_PARITY_SMOKE_OK'
