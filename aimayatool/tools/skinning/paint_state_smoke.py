from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import paint_state


def run_paint_state_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolPaintStateMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint = cmds.joint(name='AIMayaToolPaintStateJoint', position=(0, 0, 0))
    cmds.skinCluster(joint, mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolPaintStateSkinCluster')
    cmds.select(mesh, replace=True)

    context = 'AIMayaToolPaintStateCtx'
    if not cmds.artAttrSkinPaintCtx(context, exists=True):
        cmds.artAttrSkinPaintCtx(context)
    cmds.setToolTo(context)

    if not paint_state.is_skin_paint_context(context):
        raise RuntimeError('paint context detection failed')
    if paint_state.require_skin_paint_context(context) != context:
        raise RuntimeError('paint context requirement did not return the active context')

    paint_state.set_opacity(0.37, context)
    if abs(paint_state.opacity(context) - 0.37) > 1e-6:
        raise RuntimeError('paint opacity round trip failed')

    paint_state.set_value(-0.25, context)
    if abs(paint_state.value(context) + 0.25) > 1e-6:
        raise RuntimeError('paint value round trip failed')

    state = paint_state.snapshot(context)
    if state['context'] != context or abs(state['opacity'] - 0.37) > 1e-6 or abs(state['value'] + 0.25) > 1e-6:
        raise RuntimeError('paint-state snapshot mismatch: %s' % state)

    try:
        paint_state.set_opacity(1.5, context)
    except ValueError:
        pass
    else:
        raise RuntimeError('invalid opacity was not rejected')

    return 'SKINNING_PAINT_STATE_ADAPTER_SMOKE_OK'
