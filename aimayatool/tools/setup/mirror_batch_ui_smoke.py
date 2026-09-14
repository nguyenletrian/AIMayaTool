from __future__ import absolute_import


def run_setup_mirror_batch_ui_smoke():
    import maya.cmds as cmds
    from . import naming_ui

    window = cmds.window()
    column = cmds.columnLayout(parent=window)
    naming_ui.build_ui()
    descendants = cmds.layout(column, query=True, childArray=True) or []
    labels = []
    stack = list(descendants)
    while stack:
        control = stack.pop()
        try:
            if cmds.objectTypeUI(control) == "button":
                labels.append(cmds.button(control, query=True, label=True))
                continue
        except Exception:
            pass
        try:
            stack.extend(cmds.layout(control, query=True, childArray=True) or [])
        except Exception:
            pass
    required = {"Mirror X", "Mirror Y", "Mirror Z"}
    missing = sorted(required.difference(labels))
    if missing:
        raise AssertionError("Missing mirror batch UI buttons: {0}".format(missing))

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
