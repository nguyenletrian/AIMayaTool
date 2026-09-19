from __future__ import absolute_import


def _plug(value, label):
    value=str(value).strip()
    if "." not in value: raise ValueError("%s must be node.attribute" % label)
    node,attr=value.rsplit(".",1)
    if not node or not attr: raise ValueError("%s must be node.attribute" % label)
    return node,attr


def normalize_modulo_sdk(driver, attrs_data):
    driver_node,driver_attr=_plug(driver,"driver")
    expanded={}
    for group, values in (attrs_data or {}).items():
        plugs=[x.strip() for x in str(group).splitlines() if x.strip()]
        for plug in plugs:
            _plug(plug,"target"); expanded[plug]={int(k):str(v).strip() for k,v in (values or {}).items() if str(v).strip()!=""}
    if not expanded: raise ValueError("attrs_data must contain target attributes")
    slots=sorted({k for values in expanded.values() for k in values})
    if not slots: raise ValueError("attrs_data must contain at least one modulo value")
    if min(slots)<0 or max(slots)>9: raise ValueError("modulo slots must be within 0..9")
    count=max(slots)+1
    return {"driver":driver_node+"."+driver_attr,"driver_node":driver_node,"driver_attr":driver_attr,"targets":expanded,"slots":slots,"modulo_count":count}


def modulo_slot(value, modulo_count):
    if modulo_count<=0: raise ValueError("modulo_count must be positive")
    return abs(int(value) % int(modulo_count))


def build_expression_plan(driver, attrs_data):
    data=normalize_modulo_sdk(driver,attrs_data); assignments={}
    for slot in data["slots"]:
        row=[]
        for plug,values in data["targets"].items():
            if slot in values:
                node,attr=_plug(plug,"target"); row.append({"target":node,"attr":attr,"value":values[slot],"offset":node+"_Modulo_Grp"})
        assignments[slot]=row
    data["assignments"]=assignments
    return data


def apply_modulo_sdk(driver, attrs_data):
    import maya.cmds as cmds
    plan=build_expression_plan(driver,attrs_data)
    if not cmds.objExists(plan["driver_node"]): raise ValueError("Missing driver: "+plan["driver_node"])
    if not cmds.attributeQuery(plan["driver_attr"],node=plan["driver_node"],exists=True): cmds.addAttr(plan["driver_node"],longName=plan["driver_attr"],attributeType="long",defaultValue=0,keyable=True)
    offsets={}
    for plug in plan["targets"]:
        target,_=_plug(plug,"target")
        if not cmds.objExists(target): raise ValueError("Missing target: "+target)
        if target not in offsets:
            name=target+"_Modulo_Grp"
            if cmds.objExists(name): offsets[target]=name
            else:
                parent=(cmds.listRelatives(target,parent=True) or [None])[0]; offset=cmds.group(empty=True,name=name); cmds.matchTransform(offset,target)
                if parent: cmds.parent(offset,parent)
                cmds.parent(target,offset); offsets[target]=offset
    branches=[]
    for slot in plan["slots"]:
        body=[]
        for item in plan["assignments"][slot]: body.append("{0}.{1}={2};".format(offsets[item["target"]],item["attr"],item["value"]))
        branches.append(("{0}if ($r == {1})\n{{\n\t{2}\n}}".format("" if not branches else "else ",slot,"".join(body))))
    script="float $val = {0};\nint $r = abs((int)$val % {1});\n{2}\n".format(plan["driver"],plan["modulo_count"],"\n".join(branches))
    expression=cmds.expression(string=script,object="",alwaysEvaluate=True,unitConversion="all")
    return {"plan":plan,"offsets":offsets,"expression":expression,"script":script}


def modulo_sdk_managed_maya_smoke():
    import maya.cmds as cmds
    driver=cmds.createNode("transform",name="AIBridgeModuloDriver"); a=cmds.createNode("transform",name="AIBridgeModuloA"); b=cmds.createNode("transform",name="AIBridgeModuloB")
    result=apply_modulo_sdk(driver+".modulo",{a+".tx\n"+b+".ry":{"0":"1","2":"3"}})
    cmds.setAttr(driver+".modulo",2); cmds.dgdirty(allPlugs=True); cmds.refresh(force=True)
    checks={"driver_attr":cmds.attributeQuery("modulo",node=driver,exists=True),"offset_a":cmds.objExists(a+"_Modulo_Grp"),"offset_b":cmds.objExists(b+"_Modulo_Grp"),"expression":cmds.objExists(result["expression"]),"modulo_count":result["plan"]["modulo_count"]==3,"slot2_a":abs(cmds.getAttr(a+"_Modulo_Grp.tx")-3.0)<1e-6,"slot2_b":abs(cmds.getAttr(b+"_Modulo_Grp.ry")-3.0)<1e-6}
    if not all(checks.values()): raise RuntimeError("ModuloSDK smoke failed: {0}".format(checks))
    return {"ok":True,"checks":checks,"expression":result["expression"],"script":result["script"]}
