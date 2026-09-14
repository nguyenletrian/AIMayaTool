from __future__ import absolute_import


def run_setup_mirror_batch_ui_smoke():
    import maya.cmds as cmds
    from . import naming_ui

    window = cmds.window()
    column = cmds.columnLayout(parent=window)
    cmds.setParent(column)
    before_buttons = set(cmds.lsUI(type="button", long=True) or [])
    naming_ui.build_ui()
    after_buttons = set(cmds.lsUI(type="button", long=True) or [])
    labels = []
    for button in sorted(after_buttons.difference(before_buttons)):
        try:
            labels.append(cmds.button(button, query=True, label=True))
        except Exception:
            pass
    required = {"Mirror X", "Mirror Y", "Mirror Z"}
    missing = sorted(required.difference(labels))
    if missing:
        raise AssertionError("Missing mirror batch UI buttons: {0}; discovered: {1}".format(missing, sorted(labels)))

    left = cmds.createNode("transform", name="arm_L_ctrl")
    right = cmds.createNode("transform", name="arm_R_ctrl")
    cmds.xform(left, worldSpace=True, translation=(3.0, 2.0, 1.0))
    cmds.select(left, replace=True)
    result = naming_ui._mirror_selected("x")
    if len(result) != 1 or result[0]["target"].rsplit("|", 1)[-1] != right:
        raise AssertionError("Mirror selection adapter returned unexpected result: {0}".format(result))
    translation = cmds.xform(right, query=True, worldSpace=True, translation=True)
    expected = (-3.0, 2.0, 1.0)
    if any(abs(actual - wanted) > 1e-6 for actual, wanted in zip(translation, expected)):
        raise AssertionError("Mirror X adapter produced unexpected translation: {0}".format(translation))

    cmds.deleteUI(window)
    return "SETUP_MIRROR_BATCH_UI_OK:4"
