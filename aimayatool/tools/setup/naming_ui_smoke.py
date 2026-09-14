from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import naming_ui as naming_ui_module


_EXPECTED_BUTTONS = (
    "Clean Joint Names",
    "Restore Joint Names",
    "Save Name Temp",
    "Restore Name Temp",
    "Move to Namespace...",
    "Remove Namespace...",
)


def _button_labels():
    labels = []
    for control in cmds.lsUI(controls=True, long=True) or []:
        try:
            if cmds.objectTypeUI(control) == "button":
                labels.append(cmds.button(control, query=True, label=True))
        except Exception:
            pass
    return labels


def run_setup_naming_ui_smoke():
    naming_ui = importlib.reload(naming_ui_module)
    window = "AIMayaToolSetupNamingUIAdapterSmoke"
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    window = cmds.window(window, title="AIMayaTool Setup Naming UI Adapter Smoke")
    cmds.columnLayout(adjustableColumn=True)
    naming_ui.build_ui()
    labels = _button_labels()
    missing = [label for label in _EXPECTED_BUTTONS if label not in labels]
    cmds.deleteUI(window)
    if missing:
        raise RuntimeError("Setup naming UI buttons missing: {0}".format(", ".join(missing)))
    return "SETUP_NAMING_UI_ADAPTER_OK:{0}".format(len(_EXPECTED_BUTTONS))
