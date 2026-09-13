from __future__ import absolute_import

import importlib
import time

import maya.cmds as cmds

from aimayatool.tools.skinning import ratio_weights


def run_skinning_performance_baseline_smoke():
    importlib.invalidate_caches()
    importlib.reload(ratio_weights)

    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(
        name='AIMayaToolPerformanceMesh',
        subdivisionsX=20,
        subdivisionsY=20,
        width=20.0,
        height=20.0,
    )[0]
    joint_a = cmds.joint(name='AIMayaToolPerformanceJointA', position=(-5.0, 0.0, 0.0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolPerformanceJointB', position=(5.0, 0.0, 0.0))
    skin_cluster = cmds.skinCluster(
        [joint_a, joint_b],
        mesh,
        toSelectedBones=True,
        normalizeWeights=1,
        name='AIMayaToolPerformanceSkin',
    )[0]

    components = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    if not components:
        raise RuntimeError('performance fixture has no vertices')

    start = time.perf_counter()
    changed = ratio_weights.apply_influence_ratios(
        skin_cluster,
        components,
        [joint_a, joint_b],
        [0.5, 0.5],
        normalize=True,
    )
    elapsed = time.perf_counter() - start

    if len(changed) != len(components):
        raise RuntimeError('ratio baseline changed %s of %s vertices' % (len(changed), len(components)))

    return 'SKINNING_PERFORMANCE_BASELINE_OK vertices=%d elapsed=%.6f' % (len(components), elapsed)
