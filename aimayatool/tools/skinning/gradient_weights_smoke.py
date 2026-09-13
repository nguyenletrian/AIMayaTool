from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import gradient_profile
from . import gradient_weights
from . import weight_profile


def run_gradient_weights_smoke():
    cmds.file(new=True, force=True)
    importlib.invalidate_caches()
    importlib.reload(weight_profile)
    importlib.reload(gradient_profile)
    importlib.reload(gradient_weights)
    mesh = cmds.polyPlane(name='AIMayaToolGradientWeightMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolGradientJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolGradientJointB', position=(1, 0, 0)); cmds.select(clear=True)
    joint_c = cmds.joint(name='AIMayaToolGradientJointC', position=(0, 0, 1))
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolGradientSkinCluster')[0]
    near = mesh + '.vtx[0]'; far = mesh + '.vtx[1]'
    for component in (near, far):
        cmds.skinPercent(skin_cluster, component, transformValue=[(joint_a, 0.2), (joint_b, 0.6), (joint_c, 0.2)], normalize=True)
    profile = 'AIMayaToolGradientWeightProfile'
    weight_profile.reset_profile(profile)
    sampler = lambda ratio: weight_profile.sample_profile(ratio, name=profile, create=False)
    changed = gradient_weights.apply_active_influence_distance_gradient(
        skin_cluster, [near, far], joint_a, [joint_a, joint_b], [0.0, 10.0], sampler=sampler, normalize=True)
    if changed != [near, far]:
        raise RuntimeError('gradient weighting changed unexpected components: %s' % changed)
    near_a = cmds.skinPercent(skin_cluster, near, query=True, transform=joint_a)
    far_a = cmds.skinPercent(skin_cluster, far, query=True, transform=joint_a)
    if near_a <= far_a:
        raise RuntimeError('gradient active influence did not decrease with distance: %s' % ((near_a, far_a),))
    return 'SKINNING_GRADIENT_WEIGHTS_SMOKE_OK'
