from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import paint_influence
from aimayatool.tools.skinning import paint_state


def run_paint_context_influence_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolPaintInfluenceMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolPaintInfluenceA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolPaintInfluenceB', position=(1, 0, 0))
    skin_cluster = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolPaintInfluenceSkinCluster')[0]
    cmds.select(mesh, replace=True)

    context = 'AIMayaToolPaintInfluenceCtx'
    if not cmds.artAttrSkinPaintCtx(context, exists=True):
        cmds.artAttrSkinPaintCtx(context)
    cmds.setToolTo(context)
    if not paint_state.is_skin_paint_context(context):
        raise RuntimeError('paint influence smoke could not activate Paint Skin context')

    active = paint_influence.set_active_influence(joint_b, context)
    if active != joint_b:
        raise RuntimeError('active influence mismatch: %s' % active)
    if paint_influence.active_influence(context) != joint_b:
        raise RuntimeError('active influence query mismatch')

    cmds.setAttr(joint_a + '.liw', False)
    cmds.setAttr(joint_b + '.liw', True)
    snapshot = paint_influence.isolate_active(mesh, context)
    if snapshot.get(joint_a) is not False or snapshot.get(joint_b) is not True:
        raise RuntimeError('isolate_active snapshot mismatch: %s' % snapshot)
    if not cmds.getAttr(joint_a + '.liw') or cmds.getAttr(joint_b + '.liw'):
        raise RuntimeError('isolate_active did not isolate current paint influence')

    restored = paint_influence.restore(snapshot)
    if restored.get(joint_a) is not False or restored.get(joint_b) is not True:
        raise RuntimeError('paint influence restore mismatch: %s' % restored)
    if cmds.getAttr(joint_a + '.liw') or not cmds.getAttr(joint_b + '.liw'):
        raise RuntimeError('paint influence lock state was not restored exactly')

    if skin_cluster is None:
        raise RuntimeError('skin cluster setup failed')
    return 'SKINNING_PAINT_CONTEXT_INFLUENCE_SMOKE_OK'
