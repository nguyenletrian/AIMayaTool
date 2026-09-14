from __future__ import absolute_import

import importlib
import maya.cmds as cmds
import aimayatool.tools.setup as setup_module


_EXPECTED_BUTTONS = (
    "Circle", "Box", "Sphere", "Diamond", "Locator", "Eye",
    "Replace Shape...", "Zero Group", "Freeze TRS", "Reset TR", "Create Joints",
    "Parent Constraint", "Point Constraint", "Orient Constraint", "Aim Constraint",
    "Create Space Switch", "Copy Attribute...", "Create RP IK", "Snap IK/FK...", "Wire IK/FK Switch...",
    "Spline IK Chain", "Object on Curve", "Joints Between...",
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


def run_setup_ui_core_parity_smoke():
    setup = importlib.reload(setup_module)
    window = "AIMayaToolSetupUIParitySmoke"
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    window = cmds.window(window, title="AIMayaTool Setup UI Parity Smoke")
    cmds.columnLayout(adjustableColumn=True)
    setup.build_ui()
    labels = _button_labels()
    missing = [label for label in _EXPECTED_BUTTONS if label not in labels]
    cmds.deleteUI(window)
    if missing:
        raise RuntimeError("Setup UI parity buttons missing: {0}".format(", ".join(missing)))
    return "SETUP_UI_CORE_PARITY_OK:{0}".format(len(_EXPECTED_BUTTONS))
