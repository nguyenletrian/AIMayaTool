from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import influences
from aimayatool.tools.skinning import max_influences


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

    # Create the skinCluster with the intended configured limit from the start.
    # Then disable enforcement so the fixture can deliberately author a vertex
    # that violates that limit without asking Maya to reinterpret the setting.
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
