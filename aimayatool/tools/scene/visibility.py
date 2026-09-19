from __future__ import absolute_import


def _objects(value):
    if isinstance(value,(list,tuple)): values=value
    else: values=str(value or "").splitlines()
    return [str(x).strip() for x in values if str(x).strip()]


def apply_visibility(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    result=[]
    for item in items or []:
        for obj in _objects((item or {}).get("objects")):
            if not cmds.objExists(obj): result.append({"object":obj,"status":"skipped_missing"}); continue
            attr=obj+".visibility"; conn=cmds.listConnections(attr,source=True,destination=False) or []; locked=cmds.getAttr(attr,lock=True)
            if not conn and not locked:
                cmds.setAttr(attr,0); result.append({"object":obj,"status":"hidden_direct"}); continue
            parents=cmds.listRelatives(obj,parent=True) or []
            if not parents: raise ValueError("Visibility fallback requires a parent: {0}".format(obj))
            parent=parents[0]
            grp=cmds.group(empty=True,name="{}_VisOffsetGrp".format(obj)); cmds.delete(cmds.parentConstraint(obj,grp)); cmds.parent(grp,parent)
            children=cmds.listRelatives(obj,children=True) or []
            if children:
                replace=cmds.group(empty=True,name="{}_VisReplaceGrp".format(obj)); cmds.delete(cmds.parentConstraint(obj,replace)); cmds.parent(children,replace); cmds.parent(replace,parent)
                constraint=cmds.parentConstraint(obj,replace,mo=True)[0]; cmds.setAttr(constraint+".interpType",2); cmds.scaleConstraint(obj,replace,mo=True)
            cmds.parent(obj,grp); cmds.setAttr(grp+".visibility",0); result.append({"object":obj,"status":"hidden_via_offset","offset":grp})
    return result


def visibility_managed_maya_smoke():
    import maya.cmds as cmds
    root=cmds.createNode("transform",name="AIBridgeVisRoot")
    direct=cmds.createNode("transform",name="AIBridgeVisDirect",parent=root)
    locked=cmds.createNode("transform",name="AIBridgeVisLocked",parent=root); cmds.setAttr(locked+".visibility",lock=True)
    result=apply_visibility([{"objects":direct+"\nAIBridgeVisMissing\n"+locked}],cmds_module=cmds)
    direct_ok=cmds.getAttr(direct+".visibility")==0
    offset=[x for x in result if x["object"]==locked and x["status"]=="hidden_via_offset"][0]["offset"]
    locked_ok=cmds.objExists(offset) and cmds.getAttr(offset+".visibility")==0 and (cmds.listRelatives(locked,parent=True) or [None])[0]==offset
    missing=sum(1 for x in result if x["status"]=="skipped_missing")==1
    smoke={"direct":direct_ok,"fallback":bool(locked_ok),"missing":missing}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
