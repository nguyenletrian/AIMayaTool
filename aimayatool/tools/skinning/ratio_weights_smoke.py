from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning.ratio_weights import apply_influence_ratios, copy_influence_ratios


def run_ratio_weights_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolRatioWeightMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolRatioJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolRatioJointB', position=(1, 0, 0)); cmds.select(clear=True)
    joint_c = cmds.joint(name='AIMayaToolRatioJointC', position=(0, 0, 1))
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolRatioSkinCluster')[0]
    source = mesh + '.vtx[0]'; target = mesh + '.vtx[1]'
    cmds.skinPercent(skin_cluster, source, transformValue=[(joint_a, 0.6), (joint_b, 0.2), (joint_c, 0.2)], normalize=True)
    cmds.skinPercent(skin_cluster, target, transformValue=[(joint_a, 0.2), (joint_b, 0.6), (joint_c, 0.2)], normalize=True)
    changed = apply_influence_ratios(skin_cluster, [target], [joint_a, joint_b], [1.0, 1.0])
    if changed != [target]: raise RuntimeError('ratio weighting did not report target: %s' % changed)
    copy_influence_ratios(skin_cluster, source, [target], [joint_a, joint_b])
    a = cmds.skinPercent(skin_cluster, target, query=True, transform=joint_a)
    b = cmds.skinPercent(skin_cluster, target, query=True, transform=joint_b)
    c = cmds.skinPercent(skin_cluster, target, query=True, transform=joint_c)
    if abs(a - 0.6) > 1e-6 or abs(b - 0.2) > 1e-6 or abs(c - 0.2) > 1e-6:
        raise RuntimeError('ratio copy changed unexpected weights: %s' % ((a, b, c),))
    return 'SKINNING_RATIO_WEIGHTS_SMOKE_OK'
