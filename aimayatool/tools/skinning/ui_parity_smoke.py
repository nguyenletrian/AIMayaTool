from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from aimayatool.tools import skinning


_WINDOW = 'AIMayaToolSkinningUIParitySmokeWindow'
_EXPECTED_BUTTONS = {
    'Add Missing Influences From Source',
    'Remove Unused Influences',
    'Replace 0',
    'Replace 1',
    'Add -0.1',
    'Add +0.1',
    'Smooth Brush',
    'Flood Current Operation',
    'Pick Paint Value',
    'Switch Add Sign',
    'Unlock Selected Influences',
    'Unlock Top 2 Influences',
    'Unlock Parent',
    'Unlock Child',
    'Switch Unlocked Joint',
    'Copy Component Weights',
    'Create Skin Proxy',
    'Create Mirrored Proxy X',
    'Copy Proxy Skin',
    'Paste Proxy Skin',
    'Match Components To Closest Faces',
    'Create Set',
    'Next Set',
    'Back Set',
    'Delete Sets',
    'Import Into Existing Skin',
    'Quick Export Skin',
    'Quick Import Existing Skin',
}


def run_skinning_ui_parity_smoke():
    # Managed-live Maya intentionally persists between tasks, so reload the UI
    # module after a git pull before constructing controls from current code.
    importlib.invalidate_caches()
    importlib.reload(skinning)

    cmds.file(new=True, force=True)
    if cmds.window(_WINDOW, exists=True):
        cmds.deleteUI(_WINDOW)
    window = cmds.window(_WINDOW, title='AIMayaTool Skinning UI Parity Smoke')
    cmds.scrollLayout(childResizable=True)
    cmds.columnLayout(adjustableColumn=True)
    skinning.build_ui()
    descendants = cmds.lsUI(controls=True, long=True) or []
    labels = set()
    for control in descendants:
        try:
            if cmds.objectTypeUI(control) == 'button':
                labels.add(cmds.button(control, query=True, label=True))
        except RuntimeError:
            pass
    missing = sorted(_EXPECTED_BUTTONS - labels)
    cmds.deleteUI(window)
    if missing:
        raise RuntimeError('Missing Skinning UI parity controls: %s' % missing)
    return 'SKINNING_UI_PARITY_SMOKE_OK'
