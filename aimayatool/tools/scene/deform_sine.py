from __future__ import annotations


def _cmds():
    import maya.cmds as cmds
    return cmds


def build_deform_sine_plan(items):
    if not isinstance(items, (list, tuple)):
        raise TypeError("items must be a list or tuple")
    plan = []
    for item in items:
        if not isinstance(item, dict):
            raise TypeError("each item must be a dict")
        parent = str(item.get("parent", "") or "").strip()
        holder = str(item.get("attrHolder", "") or "").strip()
        curve = str(item.get("curve", "") or "").strip()
        attr_name = str(item.get("attrName", "") or "").strip()
        if not holder or not curve or not attr_name:
            raise ValueError("attrHolder, curve and attrName are required")
        plan.append({"parent": parent, "attr_holder": holder, "curve": curve, "attr_name": attr_name})
    return plan


def _ensure_attr(cmds, node, name, **kwargs):
    if not cmds.attributeQuery(name, node=node, exists=True):
        cmds.addAttr(node, ln=name, **kwargs)


def apply_deform_sine(item, cmds_module=None):
    cmds = cmds_module or _cmds()
    holder, curve, attr_name = item["attr_holder"], item["curve"], item["attr_name"]
    if not cmds.objExists(holder):
        raise ValueError("Missing attrHolder: {}".format(holder))
    if not cmds.objExists(curve):
        raise ValueError("Missing curve: {}".format(curve))
    parent = item["parent"]
    if parent and not cmds.objExists(parent):
        raise ValueError("Missing parent: {}".format(parent))
    sine_handle, sine_node = cmds.nonLinear(curve, type="sine", name=curve + "_SineDeform")
    if parent:
        cmds.parent(sine_node, parent)
    separator = attr_name + "Ops"
    if not cmds.attributeQuery(separator, node=holder, exists=True):
        cmds.addAttr(holder, ln=separator, at="enum", en="--------------")
        cmds.setAttr("{}.{}".format(holder, separator), e=True, channelBox=True)
    active = attr_name + "_Active"; _ensure_attr(cmds, holder, active, at="bool", dv=0, k=True)
    offset = attr_name + "_Offset"; _ensure_attr(cmds, holder, offset, at="double", k=True)
    visible = attr_name + "_Visible"; _ensure_attr(cmds, holder, visible, at="bool", dv=0, k=True)
    cmds.connectAttr("{}.{}".format(holder, active), "{}.envelope".format(sine_handle), force=True)
    cmds.connectAttr("{}.{}".format(holder, offset), "{}.offset".format(sine_handle), force=True)
    cmds.connectAttr("{}.{}".format(holder, visible), "{}.visibility".format(sine_node), force=True)
    return {"handle": sine_handle, "deformer": sine_node, "holder": holder}


def create_deform_sines(items, cmds_module=None):
    return [apply_deform_sine(item, cmds_module) for item in build_deform_sine_plan(items)]


def deform_sine_managed_maya_smoke():
    cmds = _cmds(); cmds.file(new=True, force=True)
    holder = cmds.createNode("transform", name="SineHolder")
    parent = cmds.createNode("transform", name="SineParent")
    curve = cmds.curve(name="SineCurve", degree=1, point=[(0,0,0),(1,0,0),(2,0,0)])
    result = create_deform_sines([{"parent": parent, "attrHolder": holder, "attrName": "Wave", "curve": curve}])[0]
    attrs = all(cmds.attributeQuery("Wave" + suffix, node=holder, exists=True) for suffix in ("Ops","_Active","_Offset","_Visible"))
    connections = (cmds.isConnected(holder+".Wave_Active", result["handle"]+".envelope") and cmds.isConnected(holder+".Wave_Offset", result["handle"]+".offset") and cmds.isConnected(holder+".Wave_Visible", result["deformer"]+".visibility"))
    parented = (cmds.listRelatives(result["deformer"], parent=True) or [None])[0].split("|")[-1] == parent
    invalid_holder = invalid_curve = invalid_parent = False
    for key,value in (("attrHolder","MissingHolder"),("curve","MissingCurve"),("parent","MissingParent")):
        data={"parent":parent,"attrHolder":holder,"attrName":"Bad","curve":curve}; data[key]=value
        try: create_deform_sines([data])
        except ValueError:
            if key=="attrHolder": invalid_holder=True
            elif key=="curve": invalid_curve=True
            else: invalid_parent=True
    evidence={"created":bool(result["handle"] and result["deformer"]),"attrs":attrs,"connections":connections,"parented":parented,"invalid_holder":invalid_holder,"invalid_curve":invalid_curve,"invalid_parent":invalid_parent}
    evidence["success"]=all(evidence.values())
    if not evidence["success"]: raise AssertionError(evidence)
    return "AIBRIDGE_UI_SMOKE_OK:{}".format(evidence)
