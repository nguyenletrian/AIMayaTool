from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _split_plug(plug):
    if not plug or "." not in plug:
        raise ValueError("Expected attribute plug, got: {0}".format(plug))
    return plug.rsplit(".", 1)


def create_fold_rig(objects, end_target, destinations, driver_attr, constraint_parent=None, create_driver=True):
    cmds = _cmds(); objects = list(objects or []); destinations = list(destinations or [])
    if not objects or len(objects) != len(destinations): raise ValueError("Fold objects and destinations must be non-empty and equal length.")
    _require_node(cmds, end_target, "Fold end target")
    for node in objects: _require_node(cmds, node, "Fold object")
    for node in destinations: _require_node(cmds, node, "Fold destination")
    if constraint_parent: _require_node(cmds, constraint_parent, "Constraint parent")
    driver_node, driver_name = _split_plug(driver_attr); _require_node(cmds, driver_node, "Fold driver node"); count = len(objects)
    if not cmds.objExists(driver_attr):
        if not create_driver: raise ValueError("Fold driver attribute does not exist: {0}".format(driver_attr))
        cmds.addAttr(driver_node, longName=driver_name, attributeType="long", minValue=0, maxValue=count, defaultValue=count, keyable=True)
    targets = [end_target] + destinations; constraints = []
    for run_index, obj in enumerate(objects, start=1):
        constraint = cmds.parentConstraint(*(targets + [obj]), maintainOffset=False)[0]; cmds.setAttr(constraint + ".interpType", 2)
        if constraint_parent: cmds.parent(constraint, constraint_parent)
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        if len(aliases) != len(targets): raise RuntimeError("Fold parentConstraint target count mismatch: {0}".format(constraint))
        for attr_value in range(count + 1):
            driver_value = count - attr_value; target_index = max(0, run_index - attr_value); cmds.setAttr(driver_attr, driver_value)
            for alias in aliases: cmds.setAttr(constraint + "." + alias, 0)
            cmds.setAttr(constraint + "." + aliases[target_index], 1)
            for alias in aliases: cmds.setDrivenKeyframe(constraint + "." + alias, currentDriver=driver_attr)
        constraints.append(constraint)
    cmds.setAttr(driver_attr, count)
    return {"driver_attr": driver_attr, "objects": tuple(objects), "end_target": end_target, "destinations": tuple(destinations), "constraints": tuple(constraints)}


def _create_rope_network(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset, constraint_parent, create_driver, roll=False):
    cmds = _cmds(); objects = list(objects or []); destinations = list(destinations or [])
    if not objects or len(objects) != len(destinations): raise ValueError("Rope objects and destinations must be non-empty and equal length.")
    for node, label in ((start_target, "Rope start target"), (end_target, "Rope end target"), (orient_reference, "Rope orient reference")): _require_node(cmds, node, label)
    for node in objects: _require_node(cmds, node, "Rope object")
    for node in destinations: _require_node(cmds, node, "Rope destination")
    if constraint_parent: _require_node(cmds, constraint_parent, "Constraint parent")
    driver_node, driver_name = _split_plug(driver_attr); _require_node(cmds, driver_node, "Rope driver node"); offset = int(offset); count = len(objects); max_value = max(count - offset, 0)
    if not cmds.objExists(driver_attr):
        if not create_driver: raise ValueError("Rope driver attribute does not exist: {0}".format(driver_attr))
        cmds.addAttr(driver_node, longName=driver_name, attributeType="long", minValue=0, maxValue=max_value, defaultValue=0, keyable=True)
    prefix = driver_attr.replace(".", "_"); offset_pma = cmds.createNode("plusMinusAverage", name=prefix + "_Offset"); cmds.setAttr(offset_pma + ".operation", 1); cmds.connectAttr(driver_attr, offset_pma + ".input1D[0]", force=True); cmds.setAttr(offset_pma + ".input1D[1]", offset)
    active = offset_pma
    nodes = [offset_pma]
    if roll:
        active = cmds.createNode("plusMinusAverage", name=prefix + "_ActiveCount"); cmds.setAttr(active + ".operation", 2); cmds.setAttr(active + ".input1D[0]", count); cmds.connectAttr(offset_pma + ".output1D", active + ".input1D[1]", force=True); nodes.append(active)
    plus = cmds.createNode("plusMinusAverage", name=prefix + "_PlusOne"); cmds.setAttr(plus + ".operation", 1); cmds.connectAttr(active + ".output1D", plus + ".input1D[0]", force=True); cmds.setAttr(plus + ".input1D[1]", 1)
    inverse = cmds.createNode("multiplyDivide", name=prefix + "_Inverse"); cmds.setAttr(inverse + ".operation", 2); cmds.setAttr(inverse + ".input1X", 1); cmds.connectAttr(plus + ".output1D", inverse + ".input2X", force=True); nodes.extend([plus, inverse])
    points = []; orients = []; tag = "RopeRoll" if roll else "Rope"
    for index, (obj, destination) in enumerate(zip(objects, destinations), start=1):
        point = cmds.pointConstraint(start_target, end_target, destination, obj, maintainOffset=False)[0]; orient = cmds.orientConstraint(orient_reference, destination, obj, maintainOffset=False)[0]
        if constraint_parent: cmds.parent(point, constraint_parent); cmds.parent(orient, constraint_parent)
        pa = cmds.pointConstraint(point, query=True, weightAliasList=True) or []; oa = cmds.orientConstraint(orient, query=True, weightAliasList=True) or []
        if len(pa) < 3 or len(oa) < 2: raise RuntimeError("Rope constraint aliases are incomplete for {0}".format(obj))
        cond = cmds.createNode("condition", name=obj + "_" + tag + "Condition"); cmds.setAttr(cond + ".operation", 3); cmds.connectAttr(active + ".output1D", cond + ".firstTerm", force=True); cmds.setAttr(cond + ".secondTerm", index); cmds.setAttr(cond + ".colorIfTrueR", 1); cmds.setAttr(cond + ".colorIfFalseR", 0)
        sub = cmds.createNode("plusMinusAverage", name=obj + "_" + tag + "StartSubtract"); cmds.setAttr(sub + ".operation", 2); cmds.connectAttr(active + ".output1D", sub + ".input1D[0]", force=True); cmds.setAttr(sub + ".input1D[1]", index - 1)
        ss = cmds.createNode("multiplyDivide", name=obj + "_" + tag + "StartScale"); cmds.connectAttr(sub + ".output1D", ss + ".input1X", force=True); cmds.connectAttr(inverse + ".outputX", ss + ".input2X", force=True)
        es = cmds.createNode("multiplyDivide", name=obj + "_" + tag + "EndScale"); cmds.setAttr(es + ".input1X", index); cmds.connectAttr(inverse + ".outputX", es + ".input2X", force=True)
        sb = cmds.createNode("multiplyDivide", name=obj + "_" + tag + "StartBlend"); cmds.connectAttr(ss + ".outputX", sb + ".input1X", force=True); cmds.connectAttr(cond + ".outColorR", sb + ".input2X", force=True)
        eb = cmds.createNode("multiplyDivide", name=obj + "_" + tag + "EndBlend"); cmds.connectAttr(es + ".outputX", eb + ".input1X", force=True); cmds.connectAttr(cond + ".outColorR", eb + ".input2X", force=True)
        rev = cmds.createNode("reverse", name=obj + "_" + tag + "DestinationReverse"); cmds.connectAttr(cond + ".outColorR", rev + ".inputX", force=True)
        cmds.connectAttr(sb + ".outputX", point + "." + pa[0], force=True); cmds.connectAttr(eb + ".outputX", point + "." + pa[1], force=True); cmds.connectAttr(rev + ".outputX", point + "." + pa[2], force=True); cmds.connectAttr(cond + ".outColorR", orient + "." + oa[0], force=True); cmds.connectAttr(rev + ".outputX", orient + "." + oa[1], force=True)
        nodes.extend([cond, sub, ss, es, sb, eb, rev]); points.append(point); orients.append(orient)
    return {"driver_attr": driver_attr, "objects": tuple(objects), "destinations": tuple(destinations), "point_constraints": tuple(points), "orient_constraints": tuple(orients), "utility_nodes": tuple(nodes)}


def create_rope_straight(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset=0, constraint_parent=None, create_driver=True):
    """Progressively straighten destination-following objects as driver increases."""
    return _create_rope_network(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset, constraint_parent, create_driver, roll=False)


def create_rope_roll(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset=0, constraint_parent=None, create_driver=True):
    """Legacy RopeRoll parity: progressively return a straight chain to destinations as driver increases."""
    return _create_rope_network(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset, constraint_parent, create_driver, roll=True)


def create_spline_ik_chain(reference_nodes, name_prefix=None):
    cmds = _cmds(); references = list(reference_nodes or [])
    if len(references) < 2: raise ValueError("Spline IK requires at least two reference nodes.")
    for node in references: _require_node(cmds, node, "Spline reference")
    prefix = name_prefix or references[0]; positions = [cmds.xform(node, query=True, worldSpace=True, translation=True) for node in references]; joints = []
    for index, position in enumerate(positions, start=1): cmds.select(clear=True); joints.append(cmds.joint(position=position, name="{0}_SplineJnt_{1:02d}".format(prefix, index)))
    for index in range(1, len(joints)): cmds.parent(joints[index], joints[index - 1])
    cmds.joint(joints[0], edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True); cmds.joint(joints[-1], edit=True, orientJoint="none")
    degree = min(3, len(positions) - 1); curve = cmds.curve(degree=degree, point=positions, name=prefix + "_SplineCurve"); cmds.setAttr(curve + ".inheritsTransform", 0)
    handle, effector = cmds.ikHandle(startJoint=joints[0], endEffector=joints[-1], solver="ikSplineSolver", curve=curve, createCurve=False, parentCurve=False, name=prefix + "_SplineIKHandle")
    return {"references": tuple(references), "joints": tuple(joints), "curve": curve, "handle": handle, "effector": effector}
