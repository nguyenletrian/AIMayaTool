from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import paint_state


_OPERATION_MAP = {
    'replace': 'absolute',
    'add': 'additive',
    'smooth': 'smooth',
}
_PROFILE_MAP = {
    'soft': 'gaussian',
    'gaussian': 'gaussian',
    'poly': 'poly',
    'solid': 'solid',
    'square': 'square',
}


def _context(context=None):
    return paint_state.require_skin_paint_context(context)


def _set_operation(operation, context=None):
    context = _context(context)
    maya_operation = _OPERATION_MAP.get(operation, operation)
    cmds.artAttrSkinPaintCtx(context, edit=True, skinPaintMode=1, selectedattroper=maya_operation)
    return context


def operation(context=None):
    context = _context(context)
    return cmds.artAttrSkinPaintCtx(context, query=True, selectedattroper=True)


def replace(value, context=None):
    context = _set_operation('replace', context)
    value = float(value)
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def add(value, context=None):
    context = _set_operation('add', context)
    value = float(value)
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def smooth(profile='soft', context=None):
    context = _set_operation('smooth', context)
    requested = str(profile).lower()
    maya_profile = _PROFILE_MAP.get(requested)
    if maya_profile is None:
        raise ValueError('Unsupported stamp profile: %s' % profile)
    cmds.artAttrSkinPaintCtx(context, edit=True, stampProfile=maya_profile)
    return requested


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
