from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import copy_weights


def run_copy_weights_undo_smoke():
    importlib.invalidate_caches()
    importlib.reload(copy_weights)
    cmds.file(new=True, force=True)

    joint_a = cmds.joint(name='AIMayaToolCopyUndoJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolCopyUndoJointB', position=(1, 0, 0)); cmds.select(clear=True)
    source = cmds.polyPlane(name='AIMayaToolCopyUndoSource', subdivisionsX=1, subdivisionsY=1)[0]
    target_a = cmds.polyPlane(name='AIMayaToolCopyUndoTargetA', subdivisionsX=1, subdivisionsY=1)[0]
    target_b = cmds.polyPlane(name='AIMayaToolCopyUndoTargetB', subdivisionsX=1, subdivisionsY=1)[0]
    source_skin = cmds.skinCluster([joint_a, joint_b], source, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolCopyUndoSourceSkin')[0]
    cmds.skinPercent(source_skin, source + '.vtx[*]', transformValue=[(joint_a, 0.4), (joint_b, 0.6)], normalize=True)

    if skin.find_skin_cluster(target_a) or skin.find_skin_cluster(target_b):
        raise RuntimeError('targets unexpectedly skinned before copy')

    copied = copy_weights.copy_batch_undoable(source, [target_a, target_b])
    if len(copied) != 2 or not skin.find_skin_cluster(target_a) or not skin.find_skin_cluster(target_b):
        raise RuntimeError('undoable copy batch did not skin both targets')

    cmds.undo()
    if skin.find_skin_cluster(target_a) or skin.find_skin_cluster(target_b):
        raise RuntimeError('single undo did not revert the complete copy batch')

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_COPY_BATCH_UNDO_OK targets=2'
