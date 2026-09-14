from __future__ import absolute_import

from . import controls


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _short_name(node):
    return node.rsplit("|", 1)[-1]


def _weight_map(cmds, constraint):
    targets = cmds.parentConstraint(constraint, q=True, targetList=True) or []
    weights = cmds.parentConstraint(constraint, q=True, weightAliasList=True) or []
    return dict((_short_name(target), weight) for target, weight in zip(targets, weights))


def create_space_switch(child, parents, attr_name="space", labels=None, maintain_offset=True, slide_attr=None, slide_default=1.0, offset_suffix="_SpaceSwitchOffset"):
    """Create an enum-driven parent-constraint space switch on an offset above child.

    When maintain_offset is False a generated Default space becomes enum index 0.
    Optional slide_attr scales the selected space weight while a root-parent fallback
    receives 1-slide, matching the useful legacy blend behavior.
    """
    cmds = _cmds()
    parents = list(parents or [])
    if not parents:
        raise ValueError("At least one space parent is required.")
    _require_node(cmds, child, "Child")
    for parent in parents:
        _require_node(cmds, parent, "Space parent")
    labels = list(labels or [_short_name(parent) for parent in parents])
    if len(labels) != len(parents):
        raise ValueError("labels must match parents length.")

    offset, _ = controls.create_zero_group(child, suffix=offset_suffix)
    root_parent = (cmds.listRelatives(offset, parent=True, fullPath=True) or [None])[0]
    default_space = None
    targets = list(parents)
    enum_labels = list(labels)
    index_offset = 0
    if not maintain_offset:
        default_space = cmds.createNode("transform", name=_short_name(child) + "_DefaultSpace", parent=root_parent) if root_parent else cmds.createNode("transform", name=_short_name(child) + "_DefaultSpace")
        cmds.matchTransform(default_space, offset)
        targets.insert(0, default_space)
        enum_labels.insert(0, "Default")
        index_offset = 1

    if not cmds.attributeQuery(attr_name, node=child, exists=True):
        cmds.addAttr(child, longName=attr_name, attributeType="enum", enumName=":".join(enum_labels) + ":")
        cmds.setAttr(child + "." + attr_name, edit=True, keyable=True)
    if slide_attr and not cmds.attributeQuery(slide_attr, node=child, exists=True):
        cmds.addAttr(child, longName=slide_attr, attributeType="double", min=0.0, max=1.0, defaultValue=float(slide_default))
        cmds.setAttr(child + "." + slide_attr, edit=True, keyable=True)

    constraint = cmds.parentConstraint(*(targets + [offset]), mo=bool(maintain_offset))[0]
    cmds.setAttr(constraint + ".interpType", 2)
    weight_map = _weight_map(cmds, constraint)
    conditions = []
    for index, target in enumerate(targets):
        condition = cmds.shadingNode("condition", asUtility=True, name=_short_name(child) + "_space{0}_COND".format(index))
        cmds.connectAttr(child + "." + attr_name, condition + ".firstTerm", force=True)
        cmds.setAttr(condition + ".secondTerm", index)
        cmds.setAttr(condition + ".colorIfFalseR", 0.0)
        if slide_attr and index >= index_offset:
            cmds.connectAttr(child + "." + slide_attr, condition + ".colorIfTrueR", force=True)
        else:
            cmds.setAttr(condition + ".colorIfTrueR", 1.0)
        cmds.connectAttr(condition + ".outColorR", constraint + "." + weight_map[_short_name(target)], force=True)
        conditions.append(condition)

    slide_constraint = None
    reverse_node = None
    if slide_attr and root_parent:
        reverse_node = cmds.shadingNode("plusMinusAverage", asUtility=True, name=_short_name(child) + "_spaceSlide_PMA")
        cmds.setAttr(reverse_node + ".operation", 2)
        cmds.setAttr(reverse_node + ".input1D[0]", 1.0)
        cmds.connectAttr(child + "." + slide_attr, reverse_node + ".input1D[1]", force=True)
        slide_constraint = cmds.parentConstraint(root_parent, offset, mo=True)[0]
        cmds.setAttr(slide_constraint + ".interpType", 2)
        slide_map = _weight_map(cmds, slide_constraint)
        cmds.connectAttr(reverse_node + ".output1D", slide_constraint + "." + slide_map[_short_name(root_parent)], force=True)

    return {"offset_group": offset, "constraint": constraint, "default_space": default_space, "conditions": tuple(conditions), "slide_constraint": slide_constraint, "slide_reverse": reverse_node, "enum_labels": tuple(enum_labels)}
