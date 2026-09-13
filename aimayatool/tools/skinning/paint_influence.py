from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import paint_state


def _skin_cluster(node):
    skin_cluster = skin.find_skin_cluster(node)
    if not skin_cluster:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return skin_cluster


def lock_state(node):
    skin_cluster = _skin_cluster(node)
    return {
        influence: bool(cmds.getAttr(influence + '.liw'))
        for influence in skin.influences(skin_cluster)
        if cmds.objExists(influence + '.liw')
    }


def set_locked(influence, locked=True):
    if not cmds.objExists(influence + '.liw'):
        raise RuntimeError('Influence does not expose lockInfluenceWeights: %s' % influence)
    cmds.setAttr(influence + '.liw', bool(locked))
    return bool(cmds.getAttr(influence + '.liw'))


def set_all_locked(node, locked=True):
    skin_cluster = _skin_cluster(node)
    result = {}
    for influence in skin.influences(skin_cluster):
        if cmds.objExists(influence + '.liw'):
            result[influence] = set_locked(influence, locked)
    return result


def isolate(node, active_influence):
    skin_cluster = _skin_cluster(node)
    influences = skin.influences(skin_cluster)
    if active_influence not in influences:
        raise ValueError('Influence is not bound to target: %s' % active_influence)
    previous = lock_state(node)
    for influence in influences:
        if cmds.objExists(influence + '.liw'):
            set_locked(influence, influence != active_influence)
    return previous


def restore(snapshot):
    restored = {}
    for influence, locked in (snapshot or {}).items():
        if cmds.objExists(influence + '.liw'):
            restored[influence] = set_locked(influence, locked)
    return restored


def active_influence(context=None):
    context = paint_state.require_skin_paint_context(context)
    return cmds.artAttrSkinPaintCtx(context, query=True, influence=True)


def set_active_influence(influence, context=None):
    context = paint_state.require_skin_paint_context(context)
    if not cmds.objExists(influence):
        raise RuntimeError('Influence does not exist: %s' % influence)
    cmds.artAttrSkinPaintCtx(context, edit=True, influence=influence)
    return active_influence(context)


def isolate_active(node, context=None):
    influence = active_influence(context)
    if not influence:
        raise RuntimeError('Paint Skin Weights has no active influence')
    return isolate(node, influence)
