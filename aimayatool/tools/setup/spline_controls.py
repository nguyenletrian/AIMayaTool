from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _curve_shape(cmds, curve):
    shapes = cmds.listRelatives(curve, shapes=True, noIntermediate=True, type="nurbsCurve") or []
    if not shapes:
        raise ValueError("Spline curve has no nurbsCurve shape: {0}".format(curve))
    return shapes[0]


def create_spline_curve_controls(curve, control_count, name_prefix=None, control_size=None, maximum_influences=2):
    """Create explicit control joints and animator controls that deform a spline curve.

    Control joints are sampled uniformly in curve percentage space, bound to the
    supplied curve, and each joint is driven by a simple square animator control
    through a zero group. This extracts the reusable control/skin layer from the
    legacy SplineRig builder while leaving IK-chain creation, global orientation,
    visibility and rig grouping as separate composition concerns.
    """
    cmds = _cmds()
    _require_node(cmds, curve, "Spline curve")
    count = int(control_count)
    if count < 2:
        raise ValueError("Spline curve controls require at least two controls.")
    max_influences = int(maximum_influences)
    if max_influences < 1:
        raise ValueError("maximum_influences must be at least 1.")

    shape = _curve_shape(cmds, curve)
    prefix = name_prefix or curve
    if control_size is None:
        control_size = max(float(cmds.arclen(curve)) * 0.03, 0.001)
    else:
        control_size = float(control_size)
        if control_size <= 0.0:
            raise ValueError("control_size must be greater than zero.")

    positions = []
    joints = []
    for index in range(count):
        u = float(index) / float(count - 1)
        poc = cmds.createNode("pointOnCurveInfo", name="{0}_SplinePOC_{1:02d}".format(prefix, index + 1))
        cmds.connectAttr(shape + ".worldSpace[0]", poc + ".inputCurve", force=True)
        cmds.setAttr(poc + ".turnOnPercentage", 1)
        cmds.setAttr(poc + ".parameter", u)
        position = cmds.getAttr(poc + ".position")[0]
        cmds.delete(poc)
        positions.append(position)
        cmds.select(clear=True)
        joint = cmds.joint(position=position, name="{0}_SplineCtrlJnt_{1:02d}".format(prefix, index + 1))
        joints.append(joint)

    skin = cmds.skinCluster(*(joints + [curve]), toSelectedBones=True, maximumInfluences=max_influences, name=prefix + "_SplineSkin")[0]

    controls = []
    zero_groups = []
    constraints = []
    points = [(-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1)]
    for index, (joint, position) in enumerate(zip(joints, positions), start=1):
        control = cmds.curve(degree=1, point=points, name="{0}_SplineCtrl_{1:02d}".format(prefix, index))
        cmds.scale(control_size, control_size, control_size, control)
        cmds.makeIdentity(control, apply=True, translate=False, rotate=False, scale=True, normal=False)
        zero = cmds.group(control, name=control + "_Zero")
        cmds.xform(zero, worldSpace=True, translation=position)
        constraint = cmds.parentConstraint(control, joint, maintainOffset=False)[0]
        controls.append(control)
        zero_groups.append(zero)
        constraints.append(constraint)

    return {
        "curve": curve,
        "curve_shape": shape,
        "control_joints": tuple(joints),
        "controls": tuple(controls),
        "zero_groups": tuple(zero_groups),
        "constraints": tuple(constraints),
        "skin_cluster": skin,
        "control_size": control_size,
    }
