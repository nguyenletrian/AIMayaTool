from __future__ import absolute_import


def _names(value, separator=None):
    if isinstance(value, str):
        value = value.split(separator) if separator else value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]


def plan_space_switch(children, parents, attr_pick="space", enum=None, attr_slide="", default_value=1.0, maintain=True):
    children, parents = _names(children), _names(parents)
    if not children: raise ValueError("children must not be empty")
    if not parents: raise ValueError("parents must not be empty")
    if len(set(children)) != len(children) or len(set(parents)) != len(parents): raise ValueError("duplicate names are ambiguous")
    attr_pick, attr_slide = str(attr_pick).strip(), str(attr_slide).strip()
    if not attr_pick: raise ValueError("attr_pick must not be empty")
    labels = _names(enum, ";") if enum else list(parents)
    if len(labels) != len(parents): raise ValueError("enum labels must match parent count")
    if len(set(labels)) != len(labels) or any(x == "Default" for x in labels): raise ValueError("enum labels must be unique and may not use Default")
    default_value = float(default_value)
    if attr_slide and not 0.0 <= default_value <= 1.0: raise ValueError("default_value must be within 0..1 when slide is enabled")
    start = 0 if maintain else 1
    options = labels if maintain else ["Default"] + labels
    targets = [{"parent": p, "label": labels[i], "pick_index": i + start} for i, p in enumerate(parents)]
    return {"children": children, "parents": parents, "attr_pick": attr_pick, "attr_slide": attr_slide or None, "default_value": default_value, "maintain": bool(maintain), "options": options, "default_pick_index": None if maintain else 0, "targets": targets, "slide_complement": "1-slide" if attr_slide else None}


def apply_space_switch(children, parents, attr_pick="space", enum=None, attr_slide="", default_value=1.0, maintain=True):
    import maya.cmds as cmds
    plan = plan_space_switch(children, parents, attr_pick, enum, attr_slide, default_value, maintain)
    results=[]
    for child in plan["children"]:
        if not cmds.objExists(child): raise ValueError("Missing child: {0}".format(child))
        for parent in plan["parents"]:
            if not cmds.objExists(parent): raise ValueError("Missing parent: {0}".format(parent))
        parent_before=(cmds.listRelatives(child,parent=True) or [None])[0]
        offset=cmds.group(empty=True,name=child+"_SpaceSwitchOffset")
        cmds.matchTransform(offset,child)
        if parent_before: cmds.parent(offset,parent_before)
        cmds.parent(child,offset)
        default_space=cmds.createNode("transform",name=child+"_DefaultSpace",parent=parent_before) if parent_before else cmds.createNode("transform",name=child+"_DefaultSpace")
        cmds.matchTransform(default_space,offset)
        if not cmds.attributeQuery(plan["attr_pick"],node=child,exists=True):
            cmds.addAttr(child,longName=plan["attr_pick"],attributeType="enum",enumName=":".join(plan["options"])+":",keyable=True)
        if plan["attr_slide"] and not cmds.attributeQuery(plan["attr_slide"],node=child,exists=True):
            cmds.addAttr(child,longName=plan["attr_slide"],attributeType="double",min=0,max=1,defaultValue=plan["default_value"],keyable=True)
        constraint=cmds.parentConstraint(*([default_space]+plan["parents"]+[offset]),maintainOffset=plan["maintain"])[0]
        cmds.setAttr(constraint+".interpType",2)
        aliases=cmds.parentConstraint(constraint,query=True,weightAliasList=True) or []
        targets=cmds.parentConstraint(constraint,query=True,targetList=True) or []
        weights={x.split("|")[-1]:a for x,a in zip(targets,aliases)}
        conditions=[]
        if not plan["maintain"]:
            node=cmds.createNode("condition",name=child+"_DefaultSpace_condition"); cmds.connectAttr(child+"."+plan["attr_pick"],node+".firstTerm",force=True); cmds.setAttr(node+".secondTerm",0); cmds.setAttr(node+".colorIfTrueR",1); cmds.setAttr(node+".colorIfFalseR",0); cmds.connectAttr(node+".outColorR",constraint+"."+weights[default_space.split("|")[-1]],force=True); conditions.append(node)
        for target in plan["targets"]:
            node=cmds.createNode("condition",name=child+"_"+target["label"]+"_Space_condition"); cmds.connectAttr(child+"."+plan["attr_pick"],node+".firstTerm",force=True); cmds.setAttr(node+".secondTerm",target["pick_index"]); cmds.setAttr(node+".colorIfFalseR",0)
            if plan["attr_slide"]: cmds.connectAttr(child+"."+plan["attr_slide"],node+".colorIfTrueR",force=True)
            else: cmds.setAttr(node+".colorIfTrueR",1)
            cmds.connectAttr(node+".outColorR",constraint+"."+weights[target["parent"].split("|")[-1]],force=True); conditions.append(node)
        slide_constraint=plus=None
        if plan["attr_slide"] and parent_before:
            plus=cmds.createNode("plusMinusAverage",name=child+"_SpaceSlide_pma"); cmds.setAttr(plus+".operation",2); cmds.setAttr(plus+".input1D[0]",1); cmds.connectAttr(child+"."+plan["attr_slide"],plus+".input1D[1]",force=True)
            slide_constraint=cmds.parentConstraint(parent_before,offset,maintainOffset=True)[0]; cmds.setAttr(slide_constraint+".interpType",2); alias=(cmds.parentConstraint(slide_constraint,query=True,weightAliasList=True) or [None])[0]; cmds.connectAttr(plus+".output1D",slide_constraint+"."+alias,force=True)
        results.append({"child":child,"offset":offset,"default_space":default_space,"constraint":constraint,"conditions":conditions,"slide_constraint":slide_constraint,"slide_node":plus})
    return results


def space_switch_managed_maya_smoke():
    import maya.cmds as cmds
    root=cmds.createNode("transform",name="AIBridgeSpaceRoot"); world=cmds.createNode("transform",name="AIBridgeSpaceWorld"); body=cmds.createNode("transform",name="AIBridgeSpaceBody"); child=cmds.createNode("transform",name="AIBridgeSpaceChild",parent=root)
    result=apply_space_switch(child,[world,body],attr_pick="space",attr_slide="spaceBlend",default_value=.25,maintain=False)[0]
    checks={"offset":cmds.objExists(result["offset"]),"default_space":cmds.objExists(result["default_space"]),"constraint":cmds.objExists(result["constraint"]),"pick_attr":cmds.attributeQuery("space",node=child,exists=True),"slide_attr":cmds.attributeQuery("spaceBlend",node=child,exists=True),"conditions":len(result["conditions"])==3,"slide_node":bool(result["slide_node"] and cmds.objExists(result["slide_node"])),"slide_constraint":bool(result["slide_constraint"] and cmds.objExists(result["slide_constraint"]))}
    if not all(checks.values()): raise RuntimeError("SpaceSwitch smoke failed: {0}".format(checks))
    return {"ok":True,"checks":checks,"result":result}
