from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import copy_weights
from aimayatool.tools.skinning import influences
from aimayatool.tools.skinning import max_influences
from aimayatool.tools.skinning import mirror_skin
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
    right_vertex, right_position = min(
        right_candidates,
        key=lambda item: abs(item[1][0] + left_position[0]) + abs(item[1][1] - left_position[1]) + abs(item[1][2] - left_position[2]))
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
