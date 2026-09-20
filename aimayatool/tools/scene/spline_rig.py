from __future__ import absolute_import

def _names(value):
    if isinstance(value, str):
        value = value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]

def normalize_spline_rig(data):
    data = data or {}
    parent = str(data.get("parent", "")).strip()
    parent_global = str(data.get("parentGlobal", "")).strip()
    controls = _names(data.get("controls"))
    if not parent:
        raise ValueError("parent must not be empty")
    if not parent_global:
        raise ValueError("parentGlobal must not be empty")
    if len(controls) < 2:
        raise ValueError("controls must contain at least two controls")
    number_ctrls = int(data.get("numberCtrls", 1))
    rebuild = int(data.get("rebuild", 100))
    if number_ctrls < 0:
        raise ValueError("numberCtrls must be zero or greater")
    if rebuild < 1:
        raise ValueError("rebuild must be at least 1")
    root = controls[0]
    total = number_ctrls + 2
    return {
        "parent": parent, "parentGlobal": parent_global, "controls": controls,
        "numberCtrls": number_ctrls, "rebuild": rebuild, "totalControlJoints": total,
        "parameters": [float(i) / float(total - 1) for i in range(total)],
        "splineJoints": [x + "_SplineJnt" for x in controls],
        "followGroups": [x + "_SplineRef" for x in controls],
        "offsetGroups": [x + "_SplineOffset" for x in controls],
        "curve": root + "_SplineJnt_SplineCurve",
        "rigGroup": root + "_SplineRig", "visibleGroup": root + "_SplineRigVisible",
        "hiddenGroup": root + "_SplineRigHidden", "master": root,
    }

def _match_group(cmds, node, name):
    group = cmds.group(empty=True, name=name)
    cmds.matchTransform(group, node)
    return group

def _offset_group(cmds, node, name):
    parent = (cmds.listRelatives(node, parent=True, fullPath=True) or [None])[0]
    group = _match_group(cmds, node, name)
    if parent:
        cmds.parent(group, parent)
    cmds.parent(node, group)
    return group

def _apply_spline_rig_unprotected(data):
    import maya.cmds as cmds
    plan = normalize_spline_rig(data)
    required = [plan["parent"], plan["parentGlobal"]] + plan["controls"]
    missing = [x for x in required if not cmds.objExists(x)]
    if missing:
        raise ValueError("Missing spline rig objects: " + ", ".join(missing))
    for ctrl, offset in zip(plan["controls"], plan["offsetGroups"]):
        if not cmds.objExists(offset):
            _offset_group(cmds, ctrl, offset)
    joints = []
    for ctrl, name in zip(plan["controls"], plan["splineJoints"]):
        cmds.select(clear=True)
        joints.append(cmds.joint(position=cmds.xform(ctrl, query=True, worldSpace=True, translation=True), name=name))
    for index in range(1, len(joints)):
        cmds.parent(joints[index], joints[index - 1])
    cmds.joint(joints[0], edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True)
    cmds.joint(joints[-1], edit=True, orientJoint="none")
    refs = []
    for ctrl, joint, name in zip(plan["controls"], joints, plan["followGroups"]):
        ref = _match_group(cmds, ctrl, name)
        cmds.parent(ref, joint)
        refs.append(ref)
    points = [cmds.xform(j, query=True, worldSpace=True, translation=True) for j in joints]
    degree = min(3, len(points) - 1)
    source_curve = cmds.curve(degree=degree, point=points, name=plan["curve"])
    cmds.setAttr(source_curve + ".inheritsTransform", 0)
    rebuilt = cmds.rebuildCurve(source_curve, constructionHistory=True, replaceOriginal=False, rebuildType=0, endKnots=True, keepRange=False, keepControlPoints=False, keepEndPoints=True, keepTangents=False, spans=plan["rebuild"], degree=3, tolerance=0.01)[0]
    rebuilt = cmds.rename(rebuilt, source_curve + "_Rebuild")
    ik_handle = cmds.ikHandle(startJoint=joints[0], endEffector=joints[-1], solver="ikSplineSolver", curve=rebuilt, createCurve=False, parentCurve=False)[0]
    control_joints = []
    for index, parameter in enumerate(plan["parameters"]):
        poc = cmds.createNode("pointOnCurveInfo")
        cmds.connectAttr(source_curve + ".worldSpace[0]", poc + ".inputCurve", force=True)
        cmds.setAttr(poc + ".turnOnPercentage", 1)
        cmds.setAttr(poc + ".parameter", parameter)
        position = cmds.getAttr(poc + ".position")[0]
        cmds.delete(poc)
        cmds.select(clear=True)
        control_joints.append(cmds.joint(position=position, name="%s_CtrlJnt_%02d" % (source_curve, index + 1)))
    skin = cmds.skinCluster(control_joints, source_curve, toSelectedBones=True, maximumInfluences=2)[0]
    spline_ctrls, zeros = [], []
    length = cmds.arclen(source_curve)
    for joint in control_joints:
        ctrl = cmds.curve(degree=1, point=[(-1,0,-1),(-1,0,1),(1,0,1),(1,0,-1),(-1,0,-1)], name=joint.replace("_CtrlJnt", "_Ctrl"))
        size = length * 0.03
        cmds.scale(size, size, size, ctrl)
        cmds.makeIdentity(ctrl, apply=True)
        zero = cmds.group(ctrl, name=ctrl + "_Zero")
        cmds.xform(zero, worldSpace=True, matrix=cmds.xform(joint, query=True, worldSpace=True, matrix=True))
        cmds.parentConstraint(ctrl, joint, maintainOffset=False)
        spline_ctrls.append(ctrl); zeros.append(zero)
    constraints = [cmds.parentConstraint(ref, offset, maintainOffset=True)[0] for ref, offset in zip(refs, plan["offsetGroups"])]
    rig = cmds.group(empty=True, name=plan["rigGroup"])
    visible = cmds.group(empty=True, name=plan["visibleGroup"], parent=rig)
    hidden = cmds.group(empty=True, name=plan["hiddenGroup"], parent=rig)
    cmds.setAttr(hidden + ".visibility", 0)
    global_group = _match_group(cmds, spline_ctrls[0], spline_ctrls[0] + "_SplineControls_GlobalGrp")
    cmds.parent(global_group, visible)
    cmds.parent(zeros, global_group)
    cmds.parent(source_curve, ik_handle, joints[0], control_joints, rebuilt, hidden)
    cmds.parent(rig, plan["parent"])
    master_spline = spline_ctrls[0]
    if not cmds.attributeQuery("Global", node=master_spline, exists=True):
        cmds.addAttr(master_spline, longName="Global", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
    blend = cmds.shadingNode("blendColors", asUtility=True)
    parent_con = cmds.parentConstraint(plan["parentGlobal"], global_group, maintainOffset=True)[0]
    cmds.setAttr(parent_con + ".interpType", 2)
    for attr in ("rx", "ry", "rz"):
        for src in cmds.listConnections(global_group + "." + attr, source=True, destination=False, plugs=True) or []:
            cmds.disconnectAttr(src, global_group + "." + attr)
    orient_con = cmds.orientConstraint(plan["parent"], global_group, maintainOffset=True)[0]
    for attr in ("rx", "ry", "rz"):
        for src in cmds.listConnections(global_group + "." + attr, source=True, destination=False, plugs=True) or []:
            cmds.disconnectAttr(src, global_group + "." + attr)
    cmds.connectAttr(parent_con + ".constraintRotate", blend + ".color1", force=True)
    cmds.connectAttr(orient_con + ".constraintRotate", blend + ".color2", force=True)
    cmds.connectAttr(blend + ".output", global_group + ".rotate", force=True)
    cmds.connectAttr(master_spline + ".Global", blend + ".blender", force=True)
    master = plan["master"]
    if not cmds.attributeQuery("SplineControls", node=master, exists=True):
        cmds.addAttr(master, longName="SplineControls", attributeType="bool", defaultValue=1, keyable=True)
    cmds.connectAttr(master + ".SplineControls", visible + ".visibility", force=True)
    for con in constraints:
        alias = (cmds.parentConstraint(con, query=True, weightAliasList=True) or [None])[0]
        if alias:
            cmds.connectAttr(master + ".SplineControls", con + "." + alias, force=True)
    for ctrl in plan["controls"][1:] + spline_ctrls:
        if ctrl != master and not cmds.attributeQuery("SplineControls", node=ctrl, exists=True):
            cmds.addAttr(ctrl, longName="SplineControls", proxy=master + ".SplineControls")
    return {"plan": plan, "joints": joints, "refs": refs, "curve": source_curve, "rebuiltCurve": rebuilt, "ikHandle": ik_handle, "controlJoints": control_joints, "splineControls": spline_ctrls, "skinCluster": skin, "rigGroup": rig, "visibleGroup": visible, "hiddenGroup": hidden, "globalGroup": global_group, "constraints": constraints}


def apply_spline_rig(data):
    import maya.cmds as cmds
    selection_uuids = cmds.ls(selection=True, uuid=True) or []
    try:
        return _apply_spline_rig_unprotected(data)
    finally:
        restored = []
        for node_uuid in selection_uuids:
            matches = cmds.ls(node_uuid, long=True) or []
            if matches:
                restored.append(matches[0])
        if restored:
            cmds.select(restored, replace=True)
        else:
            cmds.select(clear=True)

def spline_rig_managed_maya_smoke():
    import maya.cmds as cmds
    parent = cmds.createNode("transform", name="AIBridgeSplineParent")
    parent_global = cmds.createNode("transform", name="AIBridgeSplineGlobal")
    controls = []
    for index, x in enumerate((0.0, 5.0, 10.0)):
        ctrl = cmds.createNode("transform", name="AIBridgeSplineCtrl%d" % (index + 1))
        cmds.setAttr(ctrl + ".tx", x)
        controls.append(ctrl)
    result = apply_spline_rig({"parent": parent, "parentGlobal": parent_global, "controls": controls, "numberCtrls": 1, "rebuild": 8})
    checks = {"rig": cmds.objExists(result["rigGroup"]), "ik": cmds.objExists(result["ikHandle"]), "curve": cmds.objExists(result["curve"]), "control_count": len(result["splineControls"]) == 3, "visibility_attr": cmds.attributeQuery("SplineControls", node=controls[0], exists=True)}
    if not all(checks.values()):
        raise RuntimeError("SplineRig smoke failed: {0}".format(checks))
    return {"ok": True, "checks": checks}

def spline_rig_selection_state_managed_maya_smoke():
    """Measure whether Spline Rig construction preserves an unrelated explicit selection."""
    import maya.cmds as cmds
    parent = cmds.createNode("transform", name="AIBridgeSplineStateParent")
    parent_global = cmds.createNode("transform", name="AIBridgeSplineStateGlobal")
    controls = []
    for index, x in enumerate((0.0, 5.0, 10.0)):
        ctrl = cmds.createNode("transform", name="AIBridgeSplineStateCtrl%d" % (index + 1))
        cmds.setAttr(ctrl + ".tx", x)
        controls.append(ctrl)
    sentinel = cmds.createNode("transform", name="AIBridgeSplineStateSentinel")
    cmds.select(sentinel, replace=True)
    before = cmds.ls(selection=True, long=True) or []
    result = apply_spline_rig({"parent": parent, "parentGlobal": parent_global, "controls": controls, "numberCtrls": 1, "rebuild": 8})
    after = cmds.ls(selection=True, long=True) or []
    functional = bool(
        cmds.objExists(result["rigGroup"])
        and cmds.objExists(result["ikHandle"])
        and cmds.objExists(result["curve"])
        and len(result["splineControls"]) == 3
    )
    return {
        "operation": "spline_rig_selection_state",
        "functional": functional,
        "selection_preserved": before == after,
        "before": before,
        "after": after,
    }

