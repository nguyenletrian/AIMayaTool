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
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, maximumInfluences=3, normalizeWeights=1, name='AIMayaToolMaxInfluenceSmokeCluster')[0]
    vertex = mesh + '.vtx[0]'
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.5), (joint_b, 0.3), (joint_c, 0.2)], normalize=True)
    cmds.setAttr(skin_cluster + '.maxInfluences', 2)
    violating = max_influences.violating_vertices(mesh)
    if vertex not in violating:
        raise RuntimeError('max influence validation failed')
    fixed = max_influences.fix(mesh)
    if vertex not in fixed:
        raise RuntimeError('max influence fix did not report target vertex')
    remaining = max_influences.violating_vertices(mesh)
    if remaining:
        raise RuntimeError('max influence fix left violations: %s' % remaining)
    return 'SKINNING_MAX_INFLUENCE_SMOKE_OK'
