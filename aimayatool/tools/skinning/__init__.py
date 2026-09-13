from __future__ import absolute_import

import traceback


def _cmds():
    import maya.cmds as cmds
    return cmds


def _run(label, fn):
    cmds = _cmds()
    try:
        changed = fn()
        if isinstance(changed, (list, tuple)):
            text = ', '.join(str(item) for item in changed) if changed else 'no changes'
        else:
            text = str(changed) if changed else 'no changes'
        cmds.inViewMessage(amg='%s: %s' % (label, text), pos='midCenter', fade=True)
        return changed
    except Exception as exc:
        message = '%s failed: %s' % (label, exc)
        cmds.warning('AIMayaTool Skinning: %s' % message)
        try:
            cmds.inViewMessage(amg='<hl>%s</hl>' % message, pos='midCenter', fade=True)
        except Exception:
            pass
        traceback.print_exc()
        return None


def build_ui():
    cmds = _cmds()
    from . import brush_weight
    from . import closest_face
    from . import component_weights
    from . import copy_weights
    from . import influence_transfer
    from . import influences
    from . import max_influences
    from . import mirror_skin
    from . import paint_influence
    from . import proxy_clipboard
    from . import proxy_skin
    from . import selection_sets
    from . import skin_io
    from . import skirt_parent_interactive
    from . import utilities

    cmds.text(label='Influence management', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Add Selected Influences', command=lambda *_: _run('Added', influences.add_from_selection))
    cmds.button(label='Remove Selected Influences', command=lambda *_: _run('Removed', influences.remove_from_selection))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Add Missing Influences From Source', command=lambda *_: _run('Synced influences', influences.add_missing_from_selection))
    cmds.button(label='Remove Unused Influences', command=lambda *_: _run('Removed unused', influences.remove_unused_from_selection))
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
    cmds.button(label='Copy Component Weights', command=lambda *_: _run('Copied component weights', component_weights.copy_weights_from_selection))

    cmds.separator(height=8, style='none')
    cmds.text(label='Skirt parent workflow', align='left')
    cmds.text(label='Select parent joint first, skirt joints, then root-loop edges.', align='left')
    cmds.button(label='Run Skirt Parent', command=lambda *_: _run('Skirt parent', skirt_parent_interactive.run_from_selection))

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
    cmds.text(label='Paint Skin Weights', align='left')
    cmds.text(label='Activate Maya Paint Skin Weights for active-influence navigation.', align='left')
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=4, columnWidth4=(95, 95, 95, 95))
    cmds.button(label='Replace 0', command=lambda *_: _run('Paint replace', lambda: brush_weight.replace(0.0)))
    cmds.button(label='Replace 1', command=lambda *_: _run('Paint replace', lambda: brush_weight.replace(1.0)))
    cmds.button(label='Add -0.1', command=lambda *_: _run('Paint add', lambda: brush_weight.add(-0.1)))
    cmds.button(label='Add +0.1', command=lambda *_: _run('Paint add', lambda: brush_weight.add(0.1)))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Smooth Brush', command=lambda *_: _run('Paint smooth', brush_weight.smooth))
    cmds.button(label='Flood Current Operation', command=lambda *_: _run('Paint flood', brush_weight.flood))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Pick Paint Value', command=lambda *_: _run('Paint pick', brush_weight.pick_value))
    cmds.button(label='Switch Add Sign', command=lambda *_: _run('Paint add', brush_weight.toggle_add_sign))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Unlock Selected Influences', command=lambda *_: _run('Paint influences', paint_influence.unlock_selected_from_selection))
    cmds.button(label='Unlock Top 2 Influences', command=lambda *_: _run('Top influences', paint_influence.unlock_top_two_from_selection))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3, columnWidth3=(126, 126, 126))
    cmds.button(label='Unlock Parent', command=lambda *_: _run('Parent pair', paint_influence.unlock_parent_from_selection))
    cmds.button(label='Unlock Child', command=lambda *_: _run('Child pair', paint_influence.unlock_child_from_selection))
    cmds.button(label='Switch Unlocked Joint', command=lambda *_: _run('Active influence', paint_influence.switch_unlocked_from_selection))
    cmds.setParent('..')

    cmds.separator(height=8, style='none')
    cmds.text(label='Proxy skin', align='left')
    cmds.text(label='Select polygon faces from one skinned mesh.', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Create Skin Proxy', command=lambda *_: _run('Proxy', proxy_skin.create_proxy_from_selection))
    cmds.button(label='Create Mirrored Proxy X', command=lambda *_: _run('Mirrored proxy', proxy_skin.create_mirrored_proxy_from_selection))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Copy Proxy Skin', command=lambda *_: _run('Proxy snapshot', proxy_clipboard.copy_from_selection))
    cmds.button(label='Paste Proxy Skin', command=lambda *_: _run('Proxy paste', proxy_clipboard.paste_to_selection))
    cmds.setParent('..')
    cmds.button(label='Match Components To Closest Faces', command=lambda *_: _run('Closest faces', closest_face.match_from_selection))

    cmds.separator(height=8, style='none')
    cmds.text(label='Selection set navigation', align='left')
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=4, columnWidth4=(95, 95, 95, 95))
    cmds.button(label='Create Set', command=lambda *_: _run('Created set', selection_sets.create_from_selection))
    cmds.button(label='Next Set', command=lambda *_: _run('Set', selection_sets.next_from_selection))
    cmds.button(label='Back Set', command=lambda *_: _run('Set', selection_sets.previous_from_selection))
    cmds.button(label='Delete Sets', command=lambda *_: _run('Deleted sets', selection_sets.delete_from_selection))
    cmds.setParent('..')

    cmds.separator(height=8, style='none')
    cmds.text(label='Skin data', align='left')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Export Selected Skin Data', command=lambda *_: _run('Exported skin data', skin_io.export_selected))
    cmds.button(label='Import Selected Skin Data', command=lambda *_: _run('Imported skin data', skin_io.import_selected))
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(190, 190))
    cmds.button(label='Import Into Existing Skin', command=lambda *_: _run('Imported existing skin', skin_io.import_existing_selected))
    cmds.button(label='Quick Export Skin', command=lambda *_: _run('Quick exported skin', skin_io.export_quick_selected))
    cmds.setParent('..')
    cmds.button(label='Quick Import Existing Skin', command=lambda *_: _run('Quick imported skin', lambda: skin_io.import_quick_selected(require_existing=True)))