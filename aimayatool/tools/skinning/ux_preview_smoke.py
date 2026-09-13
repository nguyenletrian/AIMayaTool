from __future__ import absolute_import

import importlib

import maya.cmds as cmds

import aimayatool
from aimayatool.maya import skin
from aimayatool.tools.skinning import copy_weights


def run_ux_preview_smoke():
    importlib.invalidate_caches()
    importlib.reload(copy_weights)
    cmds.file(new=True, force=True)

    joint_a = cmds.joint(name='AIMayaToolUXPreviewJointA', position=(-1, 0, 0)); cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolUXPreviewJointB', position=(1, 0, 0)); cmds.select(clear=True)
    source = cmds.polyPlane(name='AIMayaToolUXPreviewSource', subdivisionsX=1, subdivisionsY=1)[0]
    target_a = cmds.polyPlane(name='AIMayaToolUXPreviewTargetA', subdivisionsX=1, subdivisionsY=1)[0]
    target_b = cmds.polyPlane(name='AIMayaToolUXPreviewTargetB', subdivisionsX=1, subdivisionsY=1)[0]
    cmds.skinCluster([joint_a, joint_b], source, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolUXPreviewSourceSkin')
    existing_target_skin = cmds.skinCluster([joint_a, joint_b], target_b, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolUXPreviewTargetBSkin')[0]

    cmds.select([source, target_a, target_b], replace=True)
    preview = copy_weights.preview_from_selection()
    if len(preview) != 2:
        raise RuntimeError('expected two preview items: %s' % preview)
    if skin.find_skin_cluster(target_a):
        raise RuntimeError('preview mutated unskinned target A')
    if skin.find_skin_cluster(target_b) != existing_target_skin:
        raise RuntimeError('preview changed existing target B skinCluster')
    if 'create skinCluster' not in preview[0] or 'reuse skinCluster' not in preview[1]:
        raise RuntimeError('preview text did not explain create/reuse behavior: %s' % preview)

    aimayatool.launch()
    labels = []
    for control in cmds.lsUI(type='button') or []:
        try:
            labels.append(cmds.button(control, query=True, label=True))
        except Exception:
            pass
    if 'Preview Copy Skin' not in labels or 'Copy Skin Weights' not in labels:
        raise RuntimeError('Copy Skin preview/execute UI controls not found')

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_UX_COPY_PREVIEW_OK targets=2'
