from __future__ import absolute_import


def _objects(value): return [x.strip() for x in str(value or "").splitlines() if x.strip()]
def _unique(cmds,name):
    if not cmds.objExists(name): return name
    i=1
    while cmds.objExists(name+str(i)): i+=1
    return name+str(i)

def apply_visibility_toggle(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    result=[]
    for data in items or []:
        ctrl=str(data.get("contentAttr") or "").strip(); attr=str(data.get("attribute") or "").strip()
        if not ctrl or not attr: raise ValueError("contentAttr and attribute are required")
        if not cmds.objExists(ctrl): result.append({"control":ctrl,"status":"skipped_missing_control"}); continue
        if not cmds.attributeQuery(attr,node=ctrl,exists=True): cmds.addAttr(ctrl,ln=attr,at="bool",dv=True,k=True)
        source=ctrl+"."+attr
        for obj in _objects(data.get("objects")):
            if not cmds.objExists(obj): result.append({"object":obj,"status":"skipped_missing"}); continue
            targets=[]
            if data.get("meshOnly"):
                targets=[obj]+(cmds.listRelatives(obj,children=True,type="mesh") or [])
            else:
                grp=cmds.group(em=True,name=_unique(cmds,obj+"_VisToggleOffsetGrp")); cmds.delete(cmds.parentConstraint(obj,grp)); parents=cmds.listRelatives(obj,parent=True,type="transform") or []
                if parents: cmds.parent(grp,parents[0])
                if data.get("ignoreChildren"):
                    children=cmds.listRelatives(obj,children=True,type="transform") or []
                    if children:
                        rep=cmds.group(em=True,name=_unique(cmds,obj+"_VisToggleReplaceGrp")); cmds.delete(cmds.parentConstraint(obj,rep));
                        if parents: cmds.parent(rep,parents[0])
                        cmds.parent(children,rep); pc=cmds.parentConstraint(obj,rep,mo=True)[0]; cmds.setAttr(pc+".interpType",2); cmds.scaleConstraint(obj,rep,mo=True)
                cmds.parent(obj,grp); targets=[grp]
            for target in targets:
                plug=target+".visibility"
                if not cmds.isConnected(source,plug): cmds.connectAttr(source,plug,force=True)
            result.append({"object":obj,"status":"connected","targets":targets})
    return result

def visibility_toggle_managed_maya_smoke():
    import maya.cmds as cmds
    root=cmds.createNode("transform",name="AIBridgeToggleRoot"); ctrl=cmds.createNode("transform",name="AIBridgeToggleCtrl",parent=root); obj=cmds.createNode("transform",name="AIBridgeToggleObj",parent=root); child=cmds.createNode("transform",name="AIBridgeToggleChild",parent=obj)
    result=apply_visibility_toggle([{"contentAttr":ctrl,"attribute":"showRig","objects":obj+"\nMissingToggleObj","ignoreChildren":True,"meshOnly":False}],cmds_module=cmds)
    source=ctrl+".showRig"; row=[x for x in result if x.get("object")==obj][0]; target=row["targets"][0]
    connected=cmds.isConnected(source,target+".visibility"); child_preserved=(cmds.listRelatives(child,parent=True) or [None])[0]!=obj; missing=any(x["status"]=="skipped_missing" for x in result); attr=cmds.objExists(source)
    smoke={"attr":attr,"connected":connected,"child_preserved":child_preserved,"missing":missing}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
