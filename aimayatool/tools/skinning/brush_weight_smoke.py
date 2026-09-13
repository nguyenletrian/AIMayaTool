from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import brush_weight
from aimayatool.tools.skinning import paint_state


def run_brush_weight_smoke():
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

    added = brush_weight.add(0.18, context)
    if abs(added - 0.18) > 1e-6 or abs(paint_state.value(context) - 0.18) > 1e-6:
        raise RuntimeError('add brush value mismatch')

    toggled = brush_weight.toggle_add_sign(context)
    if abs(toggled + 0.18) > 1e-6 or abs(paint_state.value(context) + 0.18) > 1e-6:
        raise RuntimeError('add-sign toggle mismatch')

    profile = brush_weight.smooth('soft', context)
    if profile != 'soft':
        raise RuntimeError('smooth profile result mismatch: %s' % profile)

    flooded_context = brush_weight.flood(context)
    if flooded_context != context:
        raise RuntimeError('flood did not return active context')

    return 'SKINNING_BRUSH_WEIGHT_SMOKE_OK'
