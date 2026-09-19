from __future__ import absolute_import


def _plug(value,label):
    value=str(value).strip()
    if "." not in value: raise ValueError("%s must be node.attribute" % label)
    node,attr=value.rsplit(".",1)
    if not node or not attr: raise ValueError("%s must be node.attribute" % label)
    return node,attr


def normalize_driven_key_item(item):
    driver=str((item or {}).get("driverAttr","")).strip(); _plug(driver,"driverAttr")
    listed=[x.strip() for x in str(item.get("drivenAttrs","")).splitlines() if x.strip()]
    for plug in listed: _plug(plug,"drivenAttr")
    keys=[]; seen=set()
    for raw in item.get("keyData") or []:
        dv=float(raw["driverValue"])
        if dv in seen: raise ValueError("duplicate driverValue")
        seen.add(dv); values={}
        for obj,attrs in (raw.get("drivenValues") or {}).items():
            obj=str(obj).strip()
            if not obj: raise ValueError("driven object must not be empty")
            values[obj]={str(a).strip():float(v) for a,v in attrs.items() if str(a).strip()}
        keys.append({"driverValue":dv,"drivenValues":values})
    keys.sort(key=lambda x:x["driverValue"])
    if not keys: raise ValueError("keyData must not be empty")
    objects=sorted({obj for k in keys for obj in k["drivenValues"]})
    return {"driverAttr":driver,"drivenAttrs":listed,"keyData":keys,"drivenObjects":objects,"offsets":{o:o+"_SDKGrp" for o in objects},"zeroOffsets":{o:o+"_ZeloSDKGrp" for o in objects}}


def build_driven_key_plan(items):
    return [normalize_driven_key_item(x) for x in (items or [])]


def _offset_group(cmds,obj,name):
    parent=(cmds.listRelatives(obj,parent=True) or [None])[0]; group=cmds.group(empty=True,name=name); cmds.matchTransform(group,obj)
    if parent: cmds.parent(group,parent)
    cmds.parent(obj,group); return group


def apply_driven_key(items):
    import maya.cmds as cmds
    results=[]
    for plan in build_driven_key_plan(items):
        if not cmds.objExists(plan["driverAttr"]): raise ValueError("Driver attr not found: "+plan["driverAttr"])
        offsets={}
        for obj in plan["drivenObjects"]:
            if not cmds.objExists(obj): raise ValueError("Missing driven object: "+obj)
            parent=(cmds.listRelatives(obj,parent=True) or [None])[0]
            offset=parent if parent and parent.endswith("_SDKGrp") else _offset_group(cmds,obj,plan["offsets"][obj])
            zero=plan["zeroOffsets"][obj]
            if not cmds.objExists(zero): _offset_group(cmds,offset,zero)
            offsets[obj]=offset
        keyed=[]
        for key in plan["keyData"]:
            for obj,attrs in key["drivenValues"].items():
                for attr,value in attrs.items():
                    sdk=offsets[obj]+"."+attr
                    if not cmds.attributeQuery(attr,node=offsets[obj],exists=True):
                        cmds.addAttr(offsets[obj],longName=attr,attributeType="double",keyable=True); cmds.connectAttr(sdk,obj+"."+attr,force=True)
                    cmds.setDrivenKeyframe(sdk,currentDriver=plan["driverAttr"],driverValue=key["driverValue"],value=value); cmds.keyTangent(sdk,inTangentType="linear",outTangentType="linear"); keyed.append(sdk)
        results.append({"plan":plan,"offsets":offsets,"keyed":sorted(set(keyed))})
    return results


def driven_key_managed_maya_smoke():
    import maya.cmds as cmds
    driver=cmds.createNode("transform",name="AIBridgeSDKDriver"); cmds.addAttr(driver,longName="drive",attributeType="double",keyable=True)
    driven=cmds.createNode("transform",name="AIBridgeSDKDriven")
    item={"driverAttr":driver+".drive","drivenAttrs":driven+".tx","keyData":[{"driverValue":0,"drivenValues":{driven:{"tx":1}}},{"driverValue":10,"drivenValues":{driven:{"tx":5}}}]}
    result=apply_driven_key([item])[0]; offset=result["offsets"][driven]; zero=driven+"_ZeloSDKGrp"; sdk=offset+".tx"
    cmds.setAttr(driver+".drive",0); v0=cmds.getAttr(sdk); cmds.setAttr(driver+".drive",10); v10=cmds.getAttr(sdk)
    curves=cmds.listConnections(sdk,source=True,destination=False,type="animCurve") or []; tangents=cmds.keyTangent(sdk,query=True,inTangentType=True) or []\n    child_source=cmds.connectionInfo(driven+".tx",sourceFromDestination=True) or ""; sdk_destinations=cmds.connectionInfo(sdk,destinationFromSource=True) or []
    checks={"sdk_group":cmds.objExists(offset),"zero_group":cmds.objExists(zero),"connected":child_source==sdk and driven+".tx" in sdk_destinations,"anim_curve":bool(curves),"value0":abs(v0-1)<1e-6,"value10":abs(v10-5)<1e-6,"linear":bool(tangents) and all(x=="linear" for x in tangents)}
    if not all(checks.values()): raise RuntimeError("DrivenKey smoke failed: {0}".format(checks))
    return {"ok":True,"checks":checks,"offset":offset,"zero":zero,"curves":curves}
