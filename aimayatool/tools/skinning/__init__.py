from __future__ import absolute_import

import maya.cmds as cmds

from . import copy_weights
from . import influences
from . import max_influences


def _run(label, fn):
    try:
        changed = fn()
        if isinstance(changed, (list, tuple)):
            text = ', '.join(changed) if changed else 'no changes'
        else:
            text = str(changed) if changed else 'no changes'
        cmds.inViewMessage(amg='%s: %s' % (label, text), pos='midCenter', fade=True)
    except Exception as exc:
        cmds.warning('AIMayaTool Skinning: %s' % exc)


def build_ui():
    cmds.text(label='Influence management', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Add Selected Influences', command=lambda *_: _run('Added', influences.add_from_selection))
    cmds.button(label='Remove Selected Influences', command=lambda *_: _run('Removed', influences.remove_from_selection))
    cmds.setParent('..')
    cmds.separator(height=8, style='none')
    cmds.text(label='Max influences (uses skinCluster setting)', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Check Configured Max', command=lambda *_: _run('Over max', max_influences.check_from_selection))
    cmds.button(label='Fix Configured Max', command=lambda *_: _run('Fixed', max_influences.fix_from_selection))
    cmds.setParent('..')
    cmds.separator(height=8, style='none')
    cmds.text(label='Skin transfer', align='left')
    cmds.button(label='Copy Skin Weights (Source -> Targets)', command=lambda *_: _run('Copied skin', copy_weights.copy_from_selection))
