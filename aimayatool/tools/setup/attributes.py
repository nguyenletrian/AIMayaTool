from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_attr(cmds, node, attribute, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))
    plug = "{0}.{1}".format(node, attribute)
    if not cmds.objExists(plug):
        raise ValueError("Attribute does not exist: {0}".format(plug))
    return plug


def copy_attribute_value(source, targets, attribute):
    """Copy one explicit attribute value from source to explicit targets."""
    cmds = _cmds(); targets = list(targets or [])
    if not targets:
        raise ValueError("At least one target is required.")
    source_plug = _require_attr(cmds, source, attribute, "Source")
    target_plugs = [_require_attr(cmds, target, attribute, "Target") for target in targets]
    value = cmds.getAttr(source_plug)
    for plug in target_plugs:
        cmds.setAttr(plug, value)
    return {"source": source, "targets": tuple(targets), "attribute": attribute, "value": value}
