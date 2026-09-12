from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import influences


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
