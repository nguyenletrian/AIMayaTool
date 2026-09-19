from __future__ import absolute_import

def _unique(cmds,name):
    if not cmds.objExists(name): return name
    i=1
    while cmds.objExists(name+str(i)): i+=1
    return name+str(i)

def apply_visibility_switch(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    result=[]
    for data in items or []:
        ctrl=str(data.get("contentAttr") or "").strip(); attr=str(data.get("attrPick") or "").strip(); options=[x.strip() for x in str(data.get("options") or "").split(":") if x.strip()]
        if not ctrl or not attr or not options: raise ValueError("contentAttr, attrPick and options are required")
        if not cmds.objExists(ctrl): result.append({"control":ctrl,"status":"skipped_missing_control"}); continue
        if not cmds.attributeQuery(attr,node=ctrl,exists=True): cmds.addAttr(ctrl,ln=attr,at="enum",en=":".join(options)); cmds.setAttr(ctrl+"."+attr,e=True,keyable=True)
        rows=str(data.get("objects") or "").splitlines()
        for index,_ in enumerate(options):
            if index>=len(rows) or not rows[index].strip(): continue
            condition=cmds.shadingNode("condition",asUtility=True); cmds.connectAttr(ctrl+"."+attr,condition+".firstTerm",force=True); cmds.setAttr(condition+".secondTerm",index); cmds.setAttr(condition+".colorIfTrueR",1); cmds.setAttr(condition+".colorIfFalseR",0)
            for obj in [x.strip() for x in rows[index].split(";") if x.strip()]:
                if not cmds.objExists(obj): result.append({"object":obj,"status":"skipped_missing","index":index}); continue
                if data.get("meshOnly"): targets=[obj]+(cmds.listRelatives(obj,children=True,type="mesh") or [])
                else:
                    grp=cmds.group(em=True,name=_unique(cmds,obj+"_VisSwitchOffsetGrp")); cmds.delete(cmds.parentConstraint(obj,grp)); parents=cmds.listRelatives(obj,parent=True) or []
                    if parents: cmds.parent(grp,parents[0])
                    if data.get("ignoreChildren"):
                        children=cmds.listRelatives(obj,children=True,type="transform") or []
                        if children:
                            rep=cmds.group(em=True,name=_unique(cmds,obj+"_VisSwitchReplaceGrp")); cmds.delete(cmds.parentConstraint(obj,rep));
                            if parents: cmds.parent(rep,parents[0])
                            cmds.parent(children,rep); pc=cmds.parentConstraint(obj,rep,mo=True)[0]; cmds.setAttr(pc+".interpType",2); cmds.scaleConstraint(obj,rep,mo=True)
                    cmds.parent(obj,grp); targets=[grp]
                for target in targets: cmds.connectAttr(condition+".outColorR",target+".visibility",force=True)
                result.append({"object":obj,"status":"connected","index":index,"condition":condition,"targets":targets})
    return result

def visibility_switch_managed_maya_smoke():
    import maya.cmds as cmds
    root=cmds.createNode("transform",name="AIBridgeSwitchRoot"); ctrl=cmds.createNode("transform",name="AIBridgeSwitchCtrl",parent=root); a=cmds.createNode("transform",name="AIBridgeSwitchA",parent=root); b=cmds.createNode("transform",name="AIBridgeSwitchB",parent=root)
    result=apply_visibility_switch([{"contentAttr":ctrl,"attrPick":"mode","options":"A:B","objects":a+"\n"+b+";MissingSwitchObj","ignoreChildren":False,"meshOnly":False}],cmds_module=cmds)
    rows=[x for x in result if x["status"]=="connected"]; missing=any(x["status"]=="skipped_missing" for x in result); attr=cmds.attributeQuery("mode",node=ctrl,exists=True); indices=sorted(x["index"] for x in rows)==[0,1]; connected=all(cmds.isConnected(x["condition"]+".outColorR",x["targets"][0]+".visibility") for x in rows)
    smoke={"attr":attr,"indices":indices,"connected":connected,"missing":missing}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
