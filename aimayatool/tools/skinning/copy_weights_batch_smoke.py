from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import copy_weights


def run_copy_weights_batch_smoke():
    importlib.invalidate_caches()
    importlib.reload(copy_weights)
    cmds.file(new=True, force=True)

    joint_a = cmds.joint(name='AIMayaToolCopyBatchJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolCopyBatchJointB', position=(1, 0, 0)); cmds.select(clear=True)
    source = cmds.polyPlane(name='AIMayaToolCopyBatchSource', subdivisionsX=2, subdivisionsY=2)[0]
    target_a = cmds.polyPlane(name='AIMayaToolCopyBatchTargetA', subdivisionsX=2, subdivisionsY=2)[0]
    target_b = cmds.polyPlane(name='AIMayaToolCopyBatchTargetB', subdivisionsX=2, subdivisionsY=2)[0]
    source_skin = cmds.skinCluster([joint_a, joint_b], source, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolCopyBatchSourceSkin')[0]
    cmds.skinPercent(source_skin, source + '.vtx[*]', transformValue=[(joint_a, 0.25), (joint_b, 0.75)], normalize=True)

    before_history = {target_a: list(cmds.listHistory(target_a) or []), target_b: list(cmds.listHistory(target_b) or [])}
    plan = copy_weights.plan_copy_batch(source, [target_a, target_b])
    if len(plan) != 2 or not all(item['will_create_skin'] for item in plan):
        raise RuntimeError('unexpected copy batch plan: %s' % plan)
    after_history = {target_a: list(cmds.listHistory(target_a) or []), target_b: list(cmds.listHistory(target_b) or [])}
    if before_history != after_history:
        raise RuntimeError('preview mutated target history')

    progress = []
    copied = copy_weights.copy_batch(source, [target_a, target_b], progress=lambda index, total, target, target_skin: progress.append((index, total, target, target_skin)))
    if len(copied) != 2 or [item[0] for item in progress] != [1, 2] or any(item[1] != 2 for item in progress):
        raise RuntimeError('invalid copy batch progress: %s' % progress)
    for target in (target_a, target_b):
        target_skin = skin.find_skin_cluster(target)
        if not target_skin:
            raise RuntimeError('missing target skinCluster: %s' % target)
        value_a = cmds.skinPercent(target_skin, target + '.vtx[0]', query=True, transform=joint_a)
        value_b = cmds.skinPercent(target_skin, target + '.vtx[0]', query=True, transform=joint_b)
        if abs(value_a - 0.25) > 1e-4 or abs(value_b - 0.75) > 1e-4:
            raise RuntimeError('copied weights mismatch on %s: %s %s' % (target, value_a, value_b))

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_COPY_BATCH_PREVIEW_OK targets=2 progress=2'
