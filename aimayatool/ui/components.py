from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def section(title, description=None, spacing=True):
    """Create a consistent compact section heading and optional description."""
    cmds = _cmds()
    if spacing:
        cmds.separator(height=8, style="none")
    label = cmds.text(label=title, align="left", font="boldLabelFont")
    if description:
        cmds.text(label=description, align="left")
    return label


def button_row(buttons, columns=None):
    """Create a compact row of (label, callback) buttons and restore the parent."""
    cmds = _cmds()
    items = list(buttons or [])
    if not items:
        raise ValueError("button_row requires at least one button")
    count = columns or len(items)
    if count != len(items):
        raise ValueError("button_row columns must match button count")
    row = cmds.rowLayout(numberOfColumns=count, adjustableColumn=count)
    for label, callback in items:
        if not callable(callback):
            raise TypeError("Button callback must be callable: {0}".format(label))
        cmds.button(label=label, command=callback)
    cmds.setParent("..")
    return row
