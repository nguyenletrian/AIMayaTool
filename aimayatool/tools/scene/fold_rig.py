from __future__ import absolute_import


def _names(value):
    if isinstance(value, str):
        value = value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]


def normalize_fold_rig(data):
    data = data or {}
    obj_end = str(data.get("objEnd", "")).strip()
    objects = _names(data.get("objsRun"))
    destinations = _names(data.get("destinations"))
    attr_content = str(data.get("attrContent", "")).strip()
    attr = str(data.get("attr", "")).strip()
    constraint_content = str(data.get("constraintContent", "")).strip()
    if not obj_end:
        raise ValueError("objEnd must not be empty")
    if not objects:
        raise ValueError("objsRun must not be empty")
    if len(objects) != len(destinations):
        raise ValueError("objsRun and destinations must have equal cardinality")
    if not attr_content or not attr:
        raise ValueError("attrContent and attr must not be empty")
    driver = attr_content + "." + attr
    targets = [obj_end] + destinations
    count = len(objects)
    keys = []
    for driver_value in range(count + 1):
        weights = [1.0 if index == driver_value else 0.0 for index in range(count + 1)]
        keys.append({"driverValue": driver_value, "weights": weights})
    return {
        "objEnd": obj_end,
        "objects": objects,
        "destinations": destinations,
        "attrContent": attr_content,
        "attr": attr,
        "driverAttr": driver,
        "constraintContent": constraint_content,
        "targets": targets,
        "count": count,
        "keys": keys,
    }


def apply_fold_rig(data):
    import maya.cmds as cmds

    plan = normalize_fold_rig(data)
    if not cmds.objExists(plan["attrContent"]):
        raise ValueError("Missing attrContent: " + plan["attrContent"])
    for node in plan["targets"] + plan["objects"]:
        if not cmds.objExists(node):
            raise ValueError("Missing FoldRig node: " + node)
    if plan["constraintContent"] and not cmds.objExists(plan["constraintContent"]):
        raise ValueError("Missing constraintContent: " + plan["constraintContent"])
    if not cmds.attributeQuery(plan["attr"], node=plan["attrContent"], exists=True):
        cmds.addAttr(plan["attrContent"], longName=plan["attr"], attributeType="long", minValue=0, maxValue=plan["count"], defaultValue=plan["count"], keyable=True)
    constraints = []
    for obj in plan["objects"]:
        constraint = cmds.parentConstraint(plan["targets"], obj, maintainOffset=False)[0]
        cmds.setAttr(constraint + ".interpType", 2)
        if plan["constraintContent"]:
            cmds.parent(constraint, plan["constraintContent"])
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        if len(aliases) != len(plan["targets"]):
            raise RuntimeError("Unexpected FoldRig parentConstraint weight count")
        for key in plan["keys"]:
            cmds.setAttr(plan["driverAttr"], key["driverValue"])
            for alias, value in zip(aliases, key["weights"]):
                plug = constraint + "." + alias
                cmds.setAttr(plug, value)
                cmds.setDrivenKeyframe(plug, currentDriver=plan["driverAttr"])
        constraints.append(constraint)
    cmds.setAttr(plan["driverAttr"], plan["count"])
    return {"plan": plan, "constraints": constraints}


def fold_rig_managed_maya_smoke():
    import maya.cmds as cmds

    prefix = "AIBridgeFoldRig"
    driver = cmds.createNode("transform", name=prefix + "_Driver")
    end = cmds.createNode("transform", name=prefix + "_End")
    destinations = [cmds.createNode("transform", name=prefix + "_Dest1"), cmds.createNode("transform", name=prefix + "_Dest2")]
    objects = [cmds.createNode("transform", name=prefix + "_Obj1"), cmds.createNode("transform", name=prefix + "_Obj2")]
    result = apply_fold_rig({"objEnd": end, "objsRun": "\n".join(objects), "destinations": "\n".join(destinations), "attrContent": driver, "attr": "fold"})
    checks = {"constraint_count": len(result["constraints"]) == 2, "driver_default": cmds.getAttr(driver + ".fold") == 2}
    for constraint in result["constraints"]:
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        checks[constraint + "_aliases"] = len(aliases) == 3
        checks[constraint + "_curves"] = all(bool(cmds.listConnections(constraint + "." + alias, source=True, destination=False, type="animCurve")) for alias in aliases)
    if not all(checks.values()):
        raise RuntimeError("FoldRig smoke failed: {0}".format(checks))
    return {"ok": True, "checks": checks, "constraints": result["constraints"]}
