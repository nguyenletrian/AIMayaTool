from __future__ import absolute_import

import maya.cmds as cmds


_SKIN_CONTEXT_CLASSES = ('artAttrSkin', 'artAttrSkinPaintCtx')


def current_context():
    return cmds.currentCtx()


def is_skin_paint_context(context=None):
    context = context or current_context()
    if not context:
        return False
    try:
        if cmds.artAttrSkinPaintCtx(context, exists=True):
            return True
    except RuntimeError:
        pass
    try:
        return cmds.contextInfo(context, c=True) in _SKIN_CONTEXT_CLASSES
    except RuntimeError:
        return False


def require_skin_paint_context(context=None):
    context = context or current_context()
    if not is_skin_paint_context(context):
        raise RuntimeError('Activate Maya Paint Skin Weights before using paint-state controls')
    return context


def opacity(context=None):
    context = require_skin_paint_context(context)
    return float(cmds.artAttrSkinPaintCtx(context, query=True, opacity=True))


def set_opacity(value, context=None):
    context = require_skin_paint_context(context)
    value = float(value)
    if value < 0.0 or value > 1.0:
        raise ValueError('Paint opacity must be between 0.0 and 1.0')
    cmds.artAttrSkinPaintCtx(context, edit=True, opacity=value)
    return opacity(context)


def value(context=None):
    context = require_skin_paint_context(context)
    return float(cmds.artAttrSkinPaintCtx(context, query=True, value=True))


def set_value(weight, context=None):
    context = require_skin_paint_context(context)
    weight = float(weight)
    cmds.artAttrSkinPaintCtx(context, edit=True, value=weight)
    return value(context)


def snapshot(context=None):
    context = require_skin_paint_context(context)
    return {
        'context': context,
        'opacity': opacity(context),
        'value': value(context),
    }
