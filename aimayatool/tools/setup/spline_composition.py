from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _disconnect_rotation_inputs(cmds, node):
    for attr in ("rx", "ry", "rz"):
        dst = node + "." + attr
        for src in cmds.listConnections(dst, source=True, destination=False, plugs=True) or []:
            cmds.disconnectAttr(src, dst)


def compose_spline_global(control_group, local_parent, global_parent, orientation_control, visibility_group=None, visibility_control=None, driven_constraints=None, proxy_controls=None, global_attr="Global", visibility_attr="SplineControls"):
    """Compose legacy SplineRig global/local orientation and visibility behavior.

    ``Global=0`` follows ``local_parent`` orientation and ``Global=1`` follows
    ``global_parent`` orientation while translation remains driven by the global
    parent constraint. ``SplineControls`` can drive a visible group, one-target
    follow constraints and proxy attributes on additional controls.
    """
    cmds = _cmds()
    visibility_control = visibility_control or orientation_control
    driven_constraints = list(driven_constraints or [])
    proxy_controls = list(proxy_controls or [])
    for node, label in ((control_group, "Spline control group"), (local_parent, "Spline local parent"), (global_parent, "Spline global parent"), (orientation_control, "Spline orientation control"), (visibility_control, "Spline visibility control")):
        _require_node(cmds, node, label)
    if visibility_group:
        _require_node(cmds, visibility_group, "Spline visibility group")
    for node in proxy_controls:
        _require_node(cmds, node, "Spline proxy control")
    for node in driven_constraints:
        _require_node(cmds, node, "Spline driven constraint")

    if not cmds.attributeQuery(global_attr, node=orientation_control, exists=True):
        cmds.addAttr(orientation_control, longName=global_attr, attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
    global_plug = orientation_control + "." + global_attr

    parent_constraint = cmds.parentConstraint(global_parent, control_group, maintainOffset=True)[0]
    cmds.setAttr(parent_constraint + ".interpType", 2)
    _disconnect_rotation_inputs(cmds, control_group)
    orient_constraint = cmds.orientConstraint(local_parent, control_group, maintainOffset=True)[0]
    _disconnect_rotation_inputs(cmds, control_group)

    blend = cmds.shadingNode("blendColors", asUtility=True, name=control_group + "_GlobalOrientBlend")
    cmds.connectAttr(parent_constraint + ".constraintRotate", blend + ".color1", force=True)
    cmds.connectAttr(orient_constraint + ".constraintRotate", blend + ".color2", force=True)
    cmds.connectAttr(blend + ".output", control_group + ".rotate", force=True)
    cmds.connectAttr(global_plug, blend + ".blender", force=True)

    visibility_plug = None
    if visibility_group or driven_constraints or proxy_controls:
        if not cmds.attributeQuery(visibility_attr, node=visibility_control, exists=True):
            cmds.addAttr(visibility_control, longName=visibility_attr, attributeType="bool", defaultValue=1, keyable=True)
        visibility_plug = visibility_control + "." + visibility_attr
        if visibility_group:
            cmds.connectAttr(visibility_plug, visibility_group + ".visibility", force=True)
        for constraint in driven_constraints:
            aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
            if len(aliases) != 1:
                raise ValueError("Spline follow constraint must have exactly one target: {0}".format(constraint))
            cmds.connectAttr(visibility_plug, constraint + "." + aliases[0], force=True)
        for control in proxy_controls:
            if control == visibility_control:
                continue
            if not cmds.attributeQuery(visibility_attr, node=control, exists=True):
                cmds.addAttr(control, longName=visibility_attr, proxy=visibility_plug)

    return {
        "control_group": control_group,
        "parent_constraint": parent_constraint,
        "orient_constraint": orient_constraint,
        "blend_node": blend,
        "global_attr": global_plug,
        "visibility_attr": visibility_plug,
        "driven_constraints": tuple(driven_constraints),
        "proxy_controls": tuple(proxy_controls),
    }
