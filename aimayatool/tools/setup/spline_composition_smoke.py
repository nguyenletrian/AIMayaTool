from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import spline_composition as spline_composition_module


def _composition():
    return importlib.reload(spline_composition_module)


def run_setup_spline_composition_smoke():
    composition = _composition()
    cmds.file(new=True, force=True)
    local_parent = cmds.createNode("transform", name="splineLocalParent")
    global_parent = cmds.createNode("transform", name="splineGlobalParent")
    control_group = cmds.createNode("transform", name="splineControlGlobal")
    orient_ctrl = cmds.createNode("transform", name="splineMasterControl")
    vis_ctrl = cmds.createNode("transform", name="splineSettings")
    visible_group = cmds.createNode("transform", name="splineVisible")
    proxy_ctrl = cmds.createNode("transform", name="splineProxyControl")
    follow_source = cmds.createNode("transform", name="splineFollowSource")
    follower = cmds.createNode("transform", name="splineFollower")
    follow_constraint = cmds.parentConstraint(follow_source, follower, maintainOffset=False)[0]

    result = composition.compose_spline_global(
        control_group, local_parent, global_parent, orient_ctrl,
        visibility_group=visible_group,
        visibility_control=vis_ctrl,
        driven_constraints=[follow_constraint],
        proxy_controls=[proxy_ctrl],
    )
    if not all(cmds.objExists(node) for node in (result["parent_constraint"], result["orient_constraint"], result["blend_node"])):
        raise RuntimeError("Spline composition nodes were not created.")

    cmds.setAttr(local_parent + ".rotateY", 10.0)
    cmds.setAttr(global_parent + ".rotateY", 70.0)
    cmds.setAttr(global_parent + ".translateX", 5.0)
    cmds.setAttr(orient_ctrl + ".Global", 0.0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(control_group + ".rotateY") - 10.0) > 1e-3:
        raise RuntimeError("Spline local orientation state mismatch.")
    if abs(cmds.getAttr(control_group + ".translateX") - 5.0) > 1e-3:
        raise RuntimeError("Spline global translation follow mismatch.")

    cmds.setAttr(orient_ctrl + ".Global", 1.0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(control_group + ".rotateY") - 70.0) > 1e-3:
        raise RuntimeError("Spline global orientation state mismatch.")

    alias = cmds.parentConstraint(follow_constraint, query=True, weightAliasList=True)[0]
    cmds.setAttr(vis_ctrl + ".SplineControls", 0)
    cmds.dgdirty(allPlugs=True)
    if cmds.getAttr(visible_group + ".visibility") != 0 or abs(cmds.getAttr(follow_constraint + "." + alias)) > 1e-6:
        raise RuntimeError("SplineControls off state mismatch.")
    cmds.setAttr(proxy_ctrl + ".SplineControls", 1)
    cmds.dgdirty(allPlugs=True)
    if cmds.getAttr(vis_ctrl + ".SplineControls") != 1 or cmds.getAttr(visible_group + ".visibility") != 1 or abs(cmds.getAttr(follow_constraint + "." + alias) - 1.0) > 1e-6:
        raise RuntimeError("SplineControls proxy/on state mismatch.")
    return "SETUP_SPLINE_COMPOSITION_SMOKE_OK:4"
