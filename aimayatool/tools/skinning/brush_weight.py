from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel

from aimayatool.tools.skinning import paint_state


_CONTEXT = 'artAttrSkinPaintCtx'


def _context(context=None):
    return paint_state.require_skin_paint_context(context)


def _paint_mode_select():
    mel.eval('artAttrSkinPaintModePaintSelect 1 %s;' % _CONTEXT)


def replace(value, context=None):
    context = _context(context)
    _paint_mode_select()
    mel.eval('artAttrPaintOperation %s Replace;' % _CONTEXT)
    value = float(value)
    mel.eval('artSkinSetSelectionValue %s false %s artAttrSkin;' % (value, _CONTEXT))
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def add(value, context=None):
    context = _context(context)
    _paint_mode_select()
    mel.eval('artAttrPaintOperation %s Add;' % _CONTEXT)
    value = float(value)
    mel.eval('artSkinSetSelectionValue %s false %s artAttrSkin;' % (value, _CONTEXT))
    cmds.artAttrSkinPaintCtx(context, edit=True, value=value)
    return value


def smooth(profile='soft', context=None):
    _context(context)
    _paint_mode_select()
    mel.eval('artUpdateStampProfile %s %s;' % (str(profile), _CONTEXT))
    mel.eval('artAttrPaintOperation %s Smooth;' % _CONTEXT)
    return str(profile)


def flood(context=None):
    context = _context(context)
    _paint_mode_select()
    cmds.artAttrSkinPaintCtx(context, edit=True, clear=True)
    return context


def toggle_add_sign(context=None):
    context = _context(context)
    current = paint_state.value(context)
    value = -current
    add(value, context)
    return value
