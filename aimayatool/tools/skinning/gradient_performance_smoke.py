from __future__ import absolute_import

import importlib
import time
import maya.cmds as cmds

from aimayatool.tools.skinning import gradient_weights


def run_gradient_performance_smoke():
    importlib.invalidate_caches()
    importlib.reload(gradient_weights)

    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolGradientPerfMesh', subdivisionsX=20, subdivisionsY=20)[0]
    joint_a = cmds.joint(name='AIMayaToolGradientPerfJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolGradientPerfJointB', position=(1, 0, 0)); cmds.select(clear=True)
    joint_c = cmds.joint(name='AIMayaToolGradientPerfJointC', position=(0, 0, 1))
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolGradientPerfSkinCluster')[0]

    components = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    count = len(components)
    if count != 441:
        raise RuntimeError('expected 441 vertices, got %s' % count)

    for component in components:
        cmds.skinPercent(skin_cluster, component, transformValue=[(joint_a, 0.4), (joint_b, 0.4), (joint_c, 0.2)], normalize=True)

    distances = [float(index) / float(max(1, count - 1)) for index in range(count)]
    started = time.perf_counter()
    changed = gradient_weights.apply_active_influence_distance_gradient(
        skin_cluster,
        components,
        joint_a,
        [joint_a, joint_b],
        distances,
        normalize=True,
    )
    elapsed = time.perf_counter() - started

    if len(changed) != count:
        raise RuntimeError('gradient weighting changed %s of %s vertices' % (len(changed), count))
    if elapsed <= 0.0:
        raise RuntimeError('invalid elapsed time: %s' % elapsed)

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_GRADIENT_PERFORMANCE_BASELINE_OK vertices=%d elapsed=%.6f' % (count, elapsed)
