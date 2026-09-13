from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel

from aimayatool.tools.skinning import paint_state


_CONTEXT = 'artAttrSkinPaintCtx'


def _context(context=None):
    return paint_state.require_skin_paint_context(context)


def _set_operation(operation, context=None):
    context = _context(context)
    try:
        cmds.artAttrSkinPaintCtx(context, edit=True, selectedattroper=operation)
    except (TypeError, RuntimeError):
        mel.eval('artAttrPaintOperation %s %s;' % (_CONTEXT, operation))
    return context


def replace(value, context=None):
    context = _set_operation('replace', context)
    value = float(value)
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def add(value, context=None):
    context = _set_operation('additive', context)
    value = float(value)
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def smooth(profile='soft', context=None):
    context = _set_operation('smooth', context)
    profile = str(profile)
    try:
        cmds.artAttrSkinPaintCtx(context, edit=True, stampProfile=profile)
    except (TypeError, RuntimeError):
        mel.eval('artUpdateStampProfile %s %s;' % (profile, _CONTEXT))
    return profile


def flood(context=None):
    context = _context(context)
    cmds.artAttrSkinPaintCtx(context, edit=True, clear=True)
    return context


def toggle_add_sign(context=None):
    context = _context(context)
    current = paint_state.value(context)
    value = -current
    add(value, context)
    return value
