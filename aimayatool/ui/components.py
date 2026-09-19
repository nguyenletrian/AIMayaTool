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
    items = list(buttons or [])
    if not items:
        raise ValueError("button_row requires at least one button")
    count = columns or len(items)
    if count != len(items):
        raise ValueError("button_row columns must match button count")
    for label, callback in items:
        if not callable(callback):
            raise TypeError("Button callback must be callable: {0}".format(label))
    cmds = _cmds()
    row = cmds.rowLayout(numberOfColumns=count, adjustableColumn=count)
    for label, callback in items:
        cmds.button(label=label, command=callback)
    cmds.setParent("..")
    return row


def run_action(label, fn, context="AIMayaTool"):
    """Run a UI action with consistent success/error presentation."""
    if not callable(fn):
        raise TypeError("run_action fn must be callable")
    cmds = _cmds()
    try:
        result = fn()
        if isinstance(result, (list, tuple)):
            detail = ", ".join(str(item) for item in result) if result else "no changes"
        else:
            detail = str(result) if result else "no changes"
        cmds.inViewMessage(amg="{0}: {1}".format(label, detail), pos="midCenter", fade=True)
        return result
    except Exception as exc:
        import traceback
        message = "{0} failed: {1}".format(label, exc)
        cmds.warning("{0}: {1}".format(context, message))
        try:
            cmds.inViewMessage(amg="<hl>{0}</hl>".format(message), pos="midCenter", fade=True)
        except Exception:
            pass
        traceback.print_exc()
        return None


def run_action_managed_maya_smoke():
    """Focused managed-Maya proof for shared success/error presentation."""
    success = run_action("Status success", lambda: ["one", "two"], context="AIMayaTool Smoke")
    if success != ["one", "two"]:
        raise RuntimeError("run_action did not preserve success result")
    failure = run_action("Status error", lambda: (_ for _ in ()).throw(ValueError("expected smoke error")), context="AIMayaTool Smoke")
    if failure is not None:
        raise RuntimeError("run_action did not return None for handled error")
    return "AIBRIDGE_UI_STATUS_OK:success|error"
