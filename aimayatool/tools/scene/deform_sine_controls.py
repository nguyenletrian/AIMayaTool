from __future__ import annotations


def _cmds():
    import maya.cmds as cmds
    return cmds


def build_deform_sine_controls_plan(items):
    if not isinstance(items, (list, tuple)): raise TypeError("items must be a list or tuple")
    plan=[]
    for item in items:
        if not isinstance(item, dict): raise TypeError("each item must be a dict")
        curve=str(item.get("curve","") or "").strip(); holder=str(item.get("attrHolder","") or "").strip(); attr=str(item.get("attrName","") or "").strip()
        controls=[x.strip() for x in str(item.get("controls","") or "").splitlines() if x.strip()]
        axes="".join(dict.fromkeys(str(item.get("translates","xyz") or "xyz").lower()))
        if not curve or not holder or not attr or not controls: raise ValueError("curve, controls, attrHolder and attrName are required")
        if any(x not in "xyz" for x in axes): raise ValueError("translates must contain only x, y and z")
        plan.append({"curve":curve,"controls":controls,"parent":str(item.get("parent","") or "").strip(),"translates":axes,"attr_holder":holder,"attr_name":attr})
    return plan


def _ensure_attr(cmds,node,name,**kwargs):
    if not cmds.attributeQuery(name,node=node,exists=True): cmds.addAttr(node,ln=name,**kwargs)


def apply_deform_sine_controls(item,cmds_module=None):
    cmds=cmds_module or _cmds(); curve=item["curve"]; controls=item["controls"]; holder=item["attr_holder"]; parent=item["parent"]
    for name,label in [(curve,"curve"),(holder,"attrHolder")]+[(c,"control") for c in controls]:
        if not cmds.objExists(name): raise ValueError("Missing {}: {}".format(label,name))
    if parent and not cmds.objExists(parent): raise ValueError("Missing parent: {}".format(parent))
    shapes=cmds.listRelatives(curve,s=True,ni=True) or []
    if not shapes: raise ValueError("Curve has no shape: {}".format(curve))
    root=cmds.group(em=True,n=controls[0]+"_SplineRefs"); refs=[]; offsets=[]
    for ctrl in controls:
        ref=cmds.group(em=True,n=ctrl+"_Ref"); cmds.matchTransform(ref,ctrl); cmds.setAttr(ref+".inheritsTransform",0)
        poc=cmds.createNode("pointOnCurveInfo",n=ctrl+"_POC"); cmds.connectAttr(shapes[0]+".worldSpace[0]",poc+".inputCurve",f=True); cmds.setAttr(poc+".turnOnPercentage",0)
        npc=cmds.createNode("nearestPointOnCurve",n=ctrl+"_NPC"); cmds.connectAttr(shapes[0]+".worldSpace[0]",npc+".inputCurve",f=True); cmds.setAttr(npc+".inPosition",*cmds.xform(ctrl,q=True,ws=True,t=True),type="double3"); parameter=cmds.getAttr(npc+".parameter"); cmds.delete(npc); cmds.setAttr(poc+".parameter",parameter)
        cmds.connectAttr(poc+".position",ref+".translate",f=True); cmds.parent(ref,root)
        ref_pos=cmds.group(em=True,n=ctrl+"_RefPos"); ref_pos2=cmds.group(em=True,n=ctrl+"_RefPos2"); cmds.matchTransform(ref_pos,ref); cmds.matchTransform(ref_pos2,ref); cmds.parent(ref_pos,root); cmds.parent(ref_pos2,ref_pos); cmds.pointConstraint(ref,ref_pos2,mo=True); refs.append(ref_pos2)
    if parent: cmds.parent(root,parent)
    for ctrl,ref_pos in zip(controls,refs):
        name=ctrl+"_SineDeformOffset"
        if cmds.objExists(name): offset=name
        else:
            offset=cmds.group(em=True,n=name); cmds.matchTransform(offset,ctrl); old=(cmds.listRelatives(ctrl,parent=True) or [None])[0]
            if old: cmds.parent(offset,old)
            cmds.parent(ctrl,offset)
        for axis in item["translates"]: cmds.connectAttr("{}.translate{}".format(ref_pos,axis.upper()),"{}.translate{}".format(offset,axis.upper()),f=True)
        offsets.append(offset)
    sine_handle,sine_node=cmds.nonLinear(curve,type="sine",name=curve+"_Sine")
    if parent: cmds.parent(sine_node,parent)
    attr=item["attr_name"]; sep=attr+"Ops"
    if not cmds.attributeQuery(sep,node=holder,exists=True): cmds.addAttr(holder,ln=sep,at="enum",en="--------------"); cmds.setAttr(holder+"."+sep,e=True,channelBox=True)
    active=attr+"_Active"; _ensure_attr(cmds,holder,active,at="bool",dv=0,k=True); off=attr+"_Offset"; _ensure_attr(cmds,holder,off,at="double",k=True); vis=attr+"_Visible"; _ensure_attr(cmds,holder,vis,at="bool",dv=0,k=True)
    cmds.connectAttr(holder+"."+active,sine_handle+".envelope",force=True); cmds.connectAttr(holder+"."+off,sine_handle+".offset",force=True); cmds.connectAttr(holder+"."+vis,sine_node+".visibility",force=True)
    return {"root":root,"refs":refs,"offsets":offsets,"handle":sine_handle,"deformer":sine_node}


def create_deform_sine_controls(items,cmds_module=None): return [apply_deform_sine_controls(x,cmds_module) for x in build_deform_sine_controls_plan(items)]


def deform_sine_controls_managed_maya_smoke():
    cmds=_cmds(); cmds.file(new=True,force=True); parent=cmds.createNode("transform",name="SineParent"); holder=cmds.createNode("transform",name="SineHolder"); curve=cmds.curve(name="DriverCurve",degree=1,point=[(0,0,0),(5,0,0),(10,0,0)]); a=cmds.createNode("transform",name="CtrlA"); b=cmds.createNode("transform",name="CtrlB"); cmds.xform(b,ws=True,t=(8,0,0))
    r=create_deform_sine_controls([{"curve":curve,"controls":"CtrlA\nCtrlB","parent":parent,"translates":"xz","attrHolder":holder,"attrName":"Wave"}])[0]
    hierarchy=(cmds.listRelatives(r["root"],parent=True) or [None])[0].split("|")[-1]==parent and all(cmds.objExists(x) for x in r["offsets"])
    axis_connections=all(cmds.isConnected(ref+".translate"+ax,off+".translate"+ax) for ref,off in zip(r["refs"],r["offsets"]) for ax in ("X","Z"))
    y_unconnected=all(not cmds.listConnections(off+".translateY",source=True,destination=False) for off in r["offsets"])
    attrs=all(cmds.attributeQuery("Wave"+s,node=holder,exists=True) for s in ("Ops","_Active","_Offset","_Visible"))
    sine_connections=cmds.isConnected(holder+".Wave_Active",r["handle"]+".envelope") and cmds.isConnected(holder+".Wave_Offset",r["handle"]+".offset") and cmds.isConnected(holder+".Wave_Visible",r["deformer"]+".visibility")
    ev={"created":bool(r["handle"] and r["deformer"]),"refs":len(r["refs"])==2,"hierarchy":hierarchy,"axis_connections":axis_connections,"y_unconnected":y_unconnected,"attrs":attrs,"sine_connections":sine_connections}; ev["success"]=all(ev.values())
    if not ev["success"]: raise AssertionError(ev)
    return "AIBRIDGE_UI_SMOKE_OK:{}".format(ev)
