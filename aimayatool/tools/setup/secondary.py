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
