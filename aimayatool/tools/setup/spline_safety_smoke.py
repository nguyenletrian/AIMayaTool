from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spline_composition as spline_composition_module


def _composition():
    return importlib.reload(spline_composition_module)


def _expect_value_error(callable_obj, label):
    before = set(cmds.ls(long=True) or [])
    try:
        callable_obj()
    except ValueError:
        after = set(cmds.ls(long=True) or [])
        if before != after:
            raise RuntimeError("{0} mutated the scene before failing.".format(label))
        return
    raise RuntimeError("{0} did not raise ValueError.".format(label))


def run_setup_spline_safety_smoke():
    composition = _composition()
    cmds.file(new=True, force=True)
    control_group = cmds.createNode("transform", name="splineSafetyControlGroup")
    local_parent = cmds.createNode("transform", name="splineSafetyLocal")
    global_parent = cmds.createNode("transform", name="splineSafetyGlobal")
    orient_ctrl = cmds.createNode("transform", name="splineSafetyOrient")
    vis_ctrl = cmds.createNode("transform", name="splineSafetyVisibility")
    visible_group = cmds.createNode("transform", name="splineSafetyVisible")
    proxy_ctrl = cmds.createNode("transform", name="splineSafetyProxy")
    follow_a = cmds.createNode("transform", name="splineSafetyFollowA")
    follow_b = cmds.createNode("transform", name="splineSafetyFollowB")
    follower = cmds.createNode("transform", name="splineSafetyFollower")
    one_target = cmds.parentConstraint(follow_a, follower, maintainOffset=False, name="splineSafetyOneTarget")[0]
    bad_follower = cmds.createNode("transform", name="splineSafetyBadFollower")
    two_target = cmds.parentConstraint(follow_a, follow_b, bad_follower, maintainOffset=False, name="splineSafetyTwoTarget")[0]

    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, control_group, global_parent, orient_ctrl),
        "control/local overlap",
    )
    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, local_parent, local_parent, orient_ctrl),
        "local/global overlap",
    )
    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, local_parent, global_parent, orient_ctrl, proxy_controls=[proxy_ctrl, proxy_ctrl]),
        "duplicate proxy controls",
    )
    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, local_parent, global_parent, orient_ctrl, driven_constraints=[one_target, one_target]),
        "duplicate driven constraints",
    )
    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, local_parent, global_parent, orient_ctrl, driven_constraints=[two_target]),
        "multi-target driven constraint",
    )
    cmds.addAttr(orient_ctrl, longName="BadGlobal", attributeType="bool", keyable=True)
    _expect_value_error(
        lambda: composition.compose_spline_global(control_group, local_parent, global_parent, orient_ctrl, global_attr="BadGlobal"),
        "wrong global attribute type",
    )

    result = composition.compose_spline_global(
        control_group,
        local_parent,
        global_parent,
        orient_ctrl,
        visibility_group=visible_group,
        visibility_control=vis_ctrl,
        driven_constraints=[one_target],
        proxy_controls=[proxy_ctrl],
    )
    for node in (result["parent_constraint"], result["orient_constraint"], result["blend_node"]):
        if not cmds.objExists(node):
            raise RuntimeError("Valid spline composition node missing: {0}".format(node))
    cmds.setAttr(local_parent + ".rotateY", 12.0)
    cmds.setAttr(global_parent + ".rotateY", 64.0)
    cmds.setAttr(global_parent + ".translateX", 5.0)
    cmds.setAttr(orient_ctrl + ".Global", 0.0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(control_group + ".rotateY") - 12.0) > 1e-3:
        raise RuntimeError("Valid spline local orientation mismatch.")
    cmds.setAttr(orient_ctrl + ".Global", 1.0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(control_group + ".rotateY") - 64.0) > 1e-3 or abs(cmds.getAttr(control_group + ".translateX") - 5.0) > 1e-3:
        raise RuntimeError("Valid spline global composition mismatch.")

    return "SETUP_SPLINE_SAFETY_OK:7"
