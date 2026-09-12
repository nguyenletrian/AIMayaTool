from __future__ import absolute_import

import maya.cmds as cmds

from . import influences


def _run(label, fn):
    try:
        changed = fn()
        cmds.inViewMessage(amg='%s: %s' % (label, ', '.join(changed) if changed else 'no changes'), pos='midCenter', fade=True)
    except Exception as exc:
        cmds.warning('AIMayaTool Skinning: %s' % exc)


def build_ui():
    cmds.text(label='Influence management', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Add Selected Influences', command=lambda *_: _run('Added', influences.add_from_selection))
    cmds.button(label='Remove Selected Influences', command=lambda *_: _run('Removed', influences.remove_from_selection))
    cmds.setParent('..')
