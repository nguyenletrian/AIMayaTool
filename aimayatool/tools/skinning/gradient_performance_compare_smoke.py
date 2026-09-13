from __future__ import absolute_import

import importlib
import time
import maya.cmds as cmds

from aimayatool.tools.skinning import gradient_weights


def _fixture(prefix):
    mesh = cmds.polyPlane(name=prefix + 'Mesh', subdivisionsX=20, subdivisionsY=20)[0]
    joint_a = cmds.joint(name=prefix + 'JointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name=prefix + 'JointB', position=(1, 0, 0)); cmds.select(clear=True)
    joint_c = cmds.joint(name=prefix + 'JointC', position=(0, 0, 1)); cmds.select(clear=True)
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, normalizeWeights=1, name=prefix + 'SkinCluster')[0]
    components = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    if len(components) != 441:
        raise RuntimeError('expected 441 vertices, got %s' % len(components))
    for component in components:
        cmds.skinPercent(skin_cluster, component, transformValue=[(joint_a, 0.4), (joint_b, 0.4), (joint_c, 0.2)], normalize=True)
    distances = [float(index) / float(max(1, len(components) - 1)) for index in range(len(components))]
    return mesh, skin_cluster, components, [joint_a, joint_b, joint_c], distances


def _weights(skin_cluster, components, joints):
    return [[cmds.skinPercent(skin_cluster, component, query=True, transform=joint) for joint in joints] for component in components]


def run_gradient_performance_compare_smoke():
    importlib.invalidate_caches()
    importlib.reload(gradient_weights)
    cmds.file(new=True, force=True)

    _, legacy_skin, legacy_components, legacy_joints, distances = _fixture('AIMayaToolGradientLegacy')
    started = time.perf_counter()
    legacy_changed = gradient_weights.apply_active_influence_distance_gradient(
        legacy_skin, legacy_components, legacy_joints[0], legacy_joints[:2], distances, normalize=True
    )
    legacy_elapsed = time.perf_counter() - started
    legacy_weights = _weights(legacy_skin, legacy_components, legacy_joints)

    _, batched_skin, batched_components, batched_joints, batched_distances = _fixture('AIMayaToolGradientBatched')
    started = time.perf_counter()
    batched_changed = gradient_weights.apply_active_influence_distance_gradient_batched(
        batched_skin, batched_components, batched_joints[0], batched_joints[:2], batched_distances, normalize=True
    )
    batched_elapsed = time.perf_counter() - started
    batched_weights = _weights(batched_skin, batched_components, batched_joints)

    if legacy_changed != legacy_components:
        raise RuntimeError('legacy changed-component reporting mismatch')
    if batched_changed != batched_components:
        raise RuntimeError('batched changed-component reporting mismatch')
    tolerance = 1e-6
    for index, (legacy_row, batched_row) in enumerate(zip(legacy_weights, batched_weights)):
        for influence_index, (legacy_value, batched_value) in enumerate(zip(legacy_row, batched_row)):
            if abs(legacy_value - batched_value) > tolerance:
                raise RuntimeError('semantic mismatch vtx=%d influence=%d legacy=%.9f batched=%.9f' % (index, influence_index, legacy_value, batched_value))
    if legacy_elapsed <= 0.0 or batched_elapsed <= 0.0:
        raise RuntimeError('invalid timing legacy=%s batched=%s' % (legacy_elapsed, batched_elapsed))
    speedup = legacy_elapsed / batched_elapsed
    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_GRADIENT_PERFORMANCE_COMPARE_OK vertices=%d legacy=%.6f batched=%.6f speedup=%.3fx' % (
        len(legacy_components), legacy_elapsed, batched_elapsed, speedup
    )
