from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import component_weights


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def run_component_weights_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolComponentWeightsMesh', subdivisionsX=2, subdivisionsY=1)[0]
    j1 = cmds.joint(name='AIMayaToolComponentWeightsJ1', position=(-1, 0, 0))
    cmds.select(clear=True)
    j2 = cmds.joint(name='AIMayaToolComponentWeightsJ2', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([j1, j2], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolComponentWeightsSkinCluster')[0]

    source = mesh + '.vtx[0]'
    target_full = mesh + '.vtx[1]'
    target_ratio = mesh + '.vtx[2]'
    cmds.skinPercent(skin_cluster, source, transformValue=[(j1, 0.8), (j2, 0.2)], normalize=True)
    cmds.skinPercent(skin_cluster, target_full, transformValue=[(j1, 0.1), (j2, 0.9)], normalize=True)
    cmds.skinPercent(skin_cluster, target_ratio, transformValue=[(j1, 0.5), (j2, 0.5)], normalize=True)

    changed = component_weights.copy_weights(source, [target_full])
    if changed != [target_full]:
        raise RuntimeError('full component copy changed-list mismatch: %s' % changed)
    if abs(_weight(skin_cluster, target_full, j1) - 0.8) > 1e-6 or abs(_weight(skin_cluster, target_full, j2) - 0.2) > 1e-6:
        raise RuntimeError('full component weight copy mismatch')

    changed = component_weights.copy_ratios(source, [target_ratio], [j1, j2])
    if changed != [target_ratio]:
        raise RuntimeError('ratio component copy changed-list mismatch: %s' % changed)
    if abs(_weight(skin_cluster, target_ratio, j1) - 0.8) > 1e-6 or abs(_weight(skin_cluster, target_ratio, j2) - 0.2) > 1e-6:
        raise RuntimeError('component ratio copy mismatch')

    try:
        component_weights.copy_weights(source, ['AIMayaToolOtherMesh.vtx[0]'])
    except (RuntimeError, ValueError):
        pass
    else:
        raise RuntimeError('invalid cross-mesh target was not rejected')

    return 'SKINNING_COMPONENT_WEIGHTS_SMOKE_OK'
