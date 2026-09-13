from __future__ import absolute_import

import maya.cmds as cmds

from . import copy_weights
from . import influence_transfer
from . import influences
from . import max_influences
from . import mirror_skin
from . import skin_io
from . import utilities


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
    cmds.button(label='Transfer Influence Weight (Source -> Target)', command=lambda *_: _run('Transferred', influence_transfer.transfer_from_selection))
    cmds.separator(height=8, style='none')
    cmds.text(label='Mirror skin across X / YZ plane', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Mirror +X Direction', command=lambda *_: _run('Mirrored skin', lambda: mirror_skin.mirror_from_selection(axis='x', inverse=False)))
    cmds.button(label='Mirror -X Direction', command=lambda *_: _run('Mirrored skin', lambda: mirror_skin.mirror_from_selection(axis='x', inverse=True)))
    cmds.setParent('..')
    cmds.separator(height=8, style='none')
    cmds.text(label='Weight utilities', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Unlock All Influences', command=lambda *_: _run('Unlocked', utilities.unlock_all_from_selection))
    cmds.button(label='Lock All Influences', command=lambda *_: _run('Locked', utilities.lock_all_from_selection))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Prune Selected Weights', command=lambda *_: _run('Pruned', utilities.prune_from_selection))
    cmds.button(label='Clear Joint From Vertices', command=lambda *_: _run('Cleared', utilities.clear_from_selection))
    cmds.setParent('..')
    cmds.button(label='Select Vertices Affected by Joints', command=lambda *_: _run('Affected vertices', utilities.select_affected_from_selection))
    cmds.separator(height=8, style='none')
    cmds.text(label='Skin data', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Export Selected Skin Data', command=lambda *_: _run('Exported skin data', skin_io.export_selected))
    cmds.button(label='Import Selected Skin Data', command=lambda *_: _run('Imported skin data', skin_io.import_selected))
    cmds.setParent('..')
