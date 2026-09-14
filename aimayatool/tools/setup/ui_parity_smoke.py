from __future__ import absolute_import

import importlib
import maya.cmds as cmds
from . import __init__ as setup_module


_EXPECTED_BUTTONS = (
    "Circle", "Box", "Sphere", "Diamond", "Locator", "Eye",
    "Replace Shape...", "Zero Group", "Freeze TRS", "Reset TR", "Create Joints",
    "Parent Constraint", "Point Constraint", "Orient Constraint", "Aim Constraint",
    "Create Space Switch", "Copy Attribute...",
)


def run_setup_ui_core_parity_smoke():
    setup = importlib.reload(setup_module)
    window = "AIMayaToolSetupUIParitySmoke"
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    window = cmds.window(window, title="AIMayaTool Setup UI Parity Smoke")
    cmds.columnLayout(adjustableColumn=True)
    setup.build_ui()
    buttons = cmds.lsUI(buttons=True, long=True) or []
    labels = []
    for button in buttons:
        try:
            labels.append(cmds.button(button, query=True, label=True))
        except Exception:
            pass
    missing = [label for label in _EXPECTED_BUTTONS if label not in labels]
    cmds.deleteUI(window)
    if missing:
        raise RuntimeError("Setup UI parity buttons missing: {0}".format(", ".join(missing)))
    return "SETUP_UI_CORE_PARITY_OK:{0}".format(len(_EXPECTED_BUTTONS))
