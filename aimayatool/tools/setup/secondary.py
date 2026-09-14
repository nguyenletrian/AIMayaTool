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
    """Create the legacy FoldRig behavior as an explicit reusable primitive.

    ``objects`` and ``destinations`` must have equal length. Each object receives
    a parentConstraint driven by ``driver_attr`` with targets ordered as
    ``[end_target] + destinations``. At driver value 0 every object follows the
    end target. As the integer driver increases, destinations are revealed from
    the end of the object chain toward the start, matching the legacy FoldRig
    driven-key choreography without UI/global state or the unused reverse node.
    """
    cmds = _cmds()
    objects = list(objects or [])
    destinations = list(destinations or [])
    if not objects or len(objects) != len(destinations):
        raise ValueError("Fold objects and destinations must be non-empty and equal length.")
    _require_node(cmds, end_target, "Fold end target")
    for node in objects:
        _require_node(cmds, node, "Fold object")
    for node in destinations:
        _require_node(cmds, node, "Fold destination")
    if constraint_parent:
        _require_node(cmds, constraint_parent, "Constraint parent")

    driver_node, driver_name = _split_plug(driver_attr)
    _require_node(cmds, driver_node, "Fold driver node")
    count = len(objects)
    if not cmds.objExists(driver_attr):
        if not create_driver:
            raise ValueError("Fold driver attribute does not exist: {0}".format(driver_attr))
        cmds.addAttr(driver_node, longName=driver_name, attributeType="long", minValue=0, maxValue=count, defaultValue=count, keyable=True)

    targets = [end_target] + destinations
    constraints = []
    for run_index, obj in enumerate(objects, start=1):
        constraint = cmds.parentConstraint(*(targets + [obj]), maintainOffset=False)[0]
        cmds.setAttr(constraint + ".interpType", 2)
        if constraint_parent:
            cmds.parent(constraint, constraint_parent)
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        if len(aliases) != len(targets):
            raise RuntimeError("Fold parentConstraint target count mismatch: {0}".format(constraint))

        for attr_value in range(count + 1):
            driver_value = count - attr_value
            target_index = max(0, run_index - attr_value)
            cmds.setAttr(driver_attr, driver_value)
            for alias in aliases:
                cmds.setAttr(constraint + "." + alias, 0)
            cmds.setAttr(constraint + "." + aliases[target_index], 1)
            for alias in aliases:
                cmds.setDrivenKeyframe(constraint + "." + alias, currentDriver=driver_attr)
        constraints.append(constraint)

    cmds.setAttr(driver_attr, count)
    return {
        "driver_attr": driver_attr,
        "objects": tuple(objects),
        "end_target": end_target,
        "destinations": tuple(destinations),
        "constraints": tuple(constraints),
    }


def create_rope_straight(objects, start_target, end_target, destinations, orient_reference, driver_attr, offset=0, constraint_parent=None, create_driver=True):
    """Create the reusable RopeStraight progressive straightening network.

    At low driver values each object follows its paired destination. As the
    integer driver advances, objects progressively blend onto the line between
    ``start_target`` and ``end_target`` while orientation switches from each
    destination to ``orient_reference``. The node math mirrors the legacy
    Scene_Pattern_RopeStraight workflow but exposes all inputs explicitly.
    """
    cmds = _cmds()
    objects = list(objects or [])
    destinations = list(destinations or [])
    if not objects or len(objects) != len(destinations):
        raise ValueError("Rope objects and destinations must be non-empty and equal length.")
    for node, label in ((start_target, "Rope start target"), (end_target, "Rope end target"), (orient_reference, "Rope orient reference")):
        _require_node(cmds, node, label)
    for node in objects:
        _require_node(cmds, node, "Rope object")
    for node in destinations:
        _require_node(cmds, node, "Rope destination")
    if constraint_parent:
        _require_node(cmds, constraint_parent, "Constraint parent")

    driver_node, driver_name = _split_plug(driver_attr)
    _require_node(cmds, driver_node, "Rope driver node")
    offset = int(offset)
    max_value = max(len(objects) - offset, 0)
    if not cmds.objExists(driver_attr):
        if not create_driver:
            raise ValueError("Rope driver attribute does not exist: {0}".format(driver_attr))
        cmds.addAttr(driver_node, longName=driver_name, attributeType="long", minValue=0, maxValue=max_value, defaultValue=0, keyable=True)

    prefix = driver_attr.replace(".", "_")
    offset_pma = cmds.createNode("plusMinusAverage", name=prefix + "_Offset")
    cmds.setAttr(offset_pma + ".operation", 1)
    cmds.connectAttr(driver_attr, offset_pma + ".input1D[0]", force=True)
    cmds.setAttr(offset_pma + ".input1D[1]", offset)

    plus = cmds.createNode("plusMinusAverage", name=prefix + "_PlusOne")
    cmds.setAttr(plus + ".operation", 1)
    cmds.connectAttr(offset_pma + ".output1D", plus + ".input1D[0]", force=True)
    cmds.setAttr(plus + ".input1D[1]", 1)

    inverse = cmds.createNode("multiplyDivide", name=prefix + "_Inverse")
    cmds.setAttr(inverse + ".operation", 2)
    cmds.setAttr(inverse + ".input1X", 1)
    cmds.connectAttr(plus + ".output1D", inverse + ".input2X", force=True)

    point_constraints = []
    orient_constraints = []
    nodes = [offset_pma, plus, inverse]
    for index, (obj, destination) in enumerate(zip(objects, destinations), start=1):
        point = cmds.pointConstraint(start_target, end_target, destination, obj, maintainOffset=False)[0]
        orient = cmds.orientConstraint(orient_reference, destination, obj, maintainOffset=False)[0]
        if constraint_parent:
            cmds.parent(point, constraint_parent)
            cmds.parent(orient, constraint_parent)
        point_aliases = cmds.pointConstraint(point, query=True, weightAliasList=True) or []
        orient_aliases = cmds.orientConstraint(orient, query=True, weightAliasList=True) or []
        if len(point_aliases) < 3 or len(orient_aliases) < 2:
            raise RuntimeError("Rope constraint aliases are incomplete for {0}".format(obj))

        condition = cmds.createNode("condition", name=obj + "_RopeCondition")
        cmds.setAttr(condition + ".operation", 3)
        cmds.connectAttr(offset_pma + ".output1D", condition + ".firstTerm", force=True)
        cmds.setAttr(condition + ".secondTerm", index)
        cmds.setAttr(condition + ".colorIfTrueR", 1)
        cmds.setAttr(condition + ".colorIfFalseR", 0)

        start_subtract = cmds.createNode("plusMinusAverage", name=obj + "_RopeStartSubtract")
        cmds.setAttr(start_subtract + ".operation", 2)
        cmds.connectAttr(offset_pma + ".output1D", start_subtract + ".input1D[0]", force=True)
        cmds.setAttr(start_subtract + ".input1D[1]", index - 1)

        start_scale = cmds.createNode("multiplyDivide", name=obj + "_RopeStartScale")
        cmds.connectAttr(start_subtract + ".output1D", start_scale + ".input1X", force=True)
        cmds.connectAttr(inverse + ".outputX", start_scale + ".input2X", force=True)

        end_scale = cmds.createNode("multiplyDivide", name=obj + "_RopeEndScale")
        cmds.setAttr(end_scale + ".input1X", index)
        cmds.connectAttr(inverse + ".outputX", end_scale + ".input2X", force=True)

        start_blend = cmds.createNode("multiplyDivide", name=obj + "_RopeStartBlend")
        cmds.connectAttr(start_scale + ".outputX", start_blend + ".input1X", force=True)
        cmds.connectAttr(condition + ".outColorR", start_blend + ".input2X", force=True)

        end_blend = cmds.createNode("multiplyDivide", name=obj + "_RopeEndBlend")
        cmds.connectAttr(end_scale + ".outputX", end_blend + ".input1X", force=True)
        cmds.connectAttr(condition + ".outColorR", end_blend + ".input2X", force=True)

        reverse = cmds.createNode("reverse", name=obj + "_RopeDestinationReverse")
        cmds.connectAttr(condition + ".outColorR", reverse + ".inputX", force=True)
        cmds.connectAttr(start_blend + ".outputX", point + "." + point_aliases[0], force=True)
        cmds.connectAttr(end_blend + ".outputX", point + "." + point_aliases[1], force=True)
        cmds.connectAttr(reverse + ".outputX", point + "." + point_aliases[2], force=True)
        cmds.connectAttr(condition + ".outColorR", orient + "." + orient_aliases[0], force=True)
        cmds.connectAttr(reverse + ".outputX", orient + "." + orient_aliases[1], force=True)

        nodes.extend([condition, start_subtract, start_scale, end_scale, start_blend, end_blend, reverse])
        point_constraints.append(point)
        orient_constraints.append(orient)

    return {
        "driver_attr": driver_attr,
        "objects": tuple(objects),
        "destinations": tuple(destinations),
        "point_constraints": tuple(point_constraints),
        "orient_constraints": tuple(orient_constraints),
        "utility_nodes": tuple(nodes),
    }
