from __future__ import absolute_import

import importlib
import time

import maya.cmds as cmds

from aimayatool.tools.skinning import ratio_weights


def _build_fixture(prefix):
    mesh = cmds.polyPlane(name=prefix + 'Mesh', subdivisionsX=20, subdivisionsY=20)[0]
    joint_a = cmds.joint(name=prefix + 'JointA', position=(-2, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name=prefix + 'JointB', position=(2, 0, 0))
    skin = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name=prefix + 'Skin')[0]
    vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(skin, vertices, transformValue=[(joint_a, 0.7), (joint_b, 0.3)], normalize=True)
    return mesh, skin, joint_a, joint_b, vertices


def _verify_weights(skin, vertices, joint_a, joint_b):
    sample_indices = [0, len(vertices) // 2, len(vertices) - 1]
    for index in sample_indices:
        vertex = vertices[index]
        a = cmds.skinPercent(skin, vertex, query=True, transform=joint_a)
        b = cmds.skinPercent(skin, vertex, query=True, transform=joint_b)
        if abs(a - 0.25) > 1e-5 or abs(b - 0.75) > 1e-5:
            raise RuntimeError('ratio mismatch at %s: %s %s' % (vertex, a, b))


def run_skinning_performance_compare_smoke():
    importlib.invalidate_caches()
    importlib.reload(ratio_weights)
    cmds.file(new=True, force=True)

    _, legacy_skin, legacy_a, legacy_b, legacy_vertices = _build_fixture('AIMayaToolPerfLegacy')
    start = time.perf_counter()
    ratio_weights.apply_influence_ratios(legacy_skin, legacy_vertices, [legacy_a, legacy_b], [0.25, 0.75])
    legacy_elapsed = time.perf_counter() - start
    _verify_weights(legacy_skin, legacy_vertices, legacy_a, legacy_b)

    _, batch_skin, batch_a, batch_b, batch_vertices = _build_fixture('AIMayaToolPerfBatch')
    start = time.perf_counter()
    ratio_weights.apply_influence_ratios_batched(batch_skin, batch_vertices, [batch_a, batch_b], [0.25, 0.75])
    batch_elapsed = time.perf_counter() - start
    _verify_weights(batch_skin, batch_vertices, batch_a, batch_b)

    speedup = legacy_elapsed / batch_elapsed if batch_elapsed > 1e-12 else 9999.0
    return 'SKINNING_PERFORMANCE_COMPARE_OK vertices=%d legacy=%.6f batched=%.6f speedup=%.3f' % (
        len(batch_vertices), legacy_elapsed, batch_elapsed, speedup)
