from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from aimayatool.tools.skinning import brush_weight
from aimayatool.tools.skinning import paint_state


def run_brush_weight_smoke():
    importlib.invalidate_caches()
    importlib.reload(brush_weight)
    importlib.reload(paint_state)
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolBrushWeightMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint = cmds.joint(name='AIMayaToolBrushWeightJoint', position=(0, 0, 0))
    cmds.skinCluster(joint, mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolBrushWeightSkinCluster')
    cmds.select(mesh, replace=True)

    context = 'AIMayaToolBrushWeightCtx'
    if not cmds.artAttrSkinPaintCtx(context, exists=True):
        cmds.artAttrSkinPaintCtx(context)
    cmds.setToolTo(context)

    if not paint_state.is_skin_paint_context(context):
        raise RuntimeError('brush smoke could not activate Paint Skin context')

    replaced = brush_weight.replace(0.42, context)
    if abs(replaced - 0.42) > 1e-6 or abs(paint_state.value(context) - 0.42) > 1e-6:
        raise RuntimeError('replace brush value mismatch')
    if brush_weight.operation(context) != 'absolute':
        raise RuntimeError('replace operation did not resolve to Maya absolute mode')

    added = brush_weight.add(0.18, context)
    if abs(added - 0.18) > 1e-6 or abs(paint_state.value(context) - 0.18) > 1e-6:
        raise RuntimeError('add brush value mismatch')
    if brush_weight.operation(context) != 'additive':
        raise RuntimeError('add operation did not resolve to Maya additive mode')

    toggled = brush_weight.toggle_add_sign(context)
    if abs(toggled + 0.18) > 1e-6 or abs(paint_state.value(context) + 0.18) > 1e-6:
        raise RuntimeError('add-sign toggle mismatch')
    if brush_weight.operation(context) != 'additive':
        raise RuntimeError('toggle did not preserve additive mode')

    picked_context = brush_weight.pick_value(context)
    if picked_context != context:
        raise RuntimeError('pick-value did not return active context')
    if brush_weight.operation(context) != 'absolute':
        raise RuntimeError('pick-value did not switch to replace mode')
    if abs(paint_state.opacity(context) - 1.0) > 1e-6:
        raise RuntimeError('pick-value did not restore full opacity')

    profile = brush_weight.smooth('soft', context)
    if profile != 'soft':
        raise RuntimeError('smooth profile result mismatch: %s' % profile)
    if brush_weight.operation(context) != 'smooth':
        raise RuntimeError('smooth operation did not resolve to Maya smooth mode')
    if cmds.artAttrSkinPaintCtx(context, query=True, stampProfile=True) != 'gaussian':
        raise RuntimeError('legacy soft profile did not map to Maya gaussian profile')

    flooded_context = brush_weight.flood(context)
    if flooded_context != context:
        raise RuntimeError('flood did not return active context')

    return 'SKINNING_BRUSH_WEIGHT_SMOKE_OK'
