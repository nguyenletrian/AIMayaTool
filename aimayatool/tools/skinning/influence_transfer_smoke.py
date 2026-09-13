from __future__ import absolute_import

import maya.cmds as cmds

from .influence_transfer import transfer_influence_weight


def run_influence_transfer_smoke():
    mesh = cmds.polyPlane(name="AIMayaTool_TransferMesh", sx=1, sy=1)[0]
    joint_a = cmds.joint(name="AIMayaTool_TransferJointA", position=[-1.0, 0.0, 0.0])
    cmds.select(clear=True)
    joint_b = cmds.joint(name="AIMayaTool_TransferJointB", position=[1.0, 0.0, 0.0])
    skin = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1)[0]
    component = mesh + ".vtx[0]"
    cmds.skinPercent(skin, component, transformValue=[(joint_a, 0.25), (joint_b, 0.75)], normalize=True)
    changed = transfer_influence_weight(skin, [component], joint_a, joint_b)
    assert changed == [component]
    source = cmds.skinPercent(skin, component, query=True, transform=joint_a)
    target = cmds.skinPercent(skin, component, query=True, transform=joint_b)
    assert abs(source) < 1e-6
    assert abs(target - 1.0) < 1e-6
    return "SKINNING_INFLUENCE_TRANSFER_SMOKE_OK"
