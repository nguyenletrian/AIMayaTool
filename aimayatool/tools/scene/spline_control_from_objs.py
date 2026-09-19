from __future__ import absolute_import

def _names(value):
    if isinstance(value,str): value=value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]

def normalize_spline_control_from_objs(data):
    data=data or {}
    parent=str(data.get("parent","")).strip(); parent_global=str(data.get("parentGlobal","")).strip()
    curve=str(data.get("curve","")).strip(); joints=_names(data.get("joints"))
    number_ctrls=int(data.get("numberCtrls",1))
    if not parent or not parent_global or not curve: raise ValueError("parent, parentGlobal and curve must not be empty")
    if len(joints)<2: raise ValueError("joints must contain at least two joints")
    if number_ctrls<0: raise ValueError("numberCtrls must be zero or greater")
    controls=[x[:-10] if x.endswith("_SplineJnt") else x for x in joints]; base=controls[0]; total=number_ctrls+2
    return {"parent":parent,"parentGlobal":parent_global,"curve":curve,"joints":joints,"controls":controls,
      "numberCtrls":number_ctrls,"totalControlJoints":total,"parameters":[float(i)/float(total-1) for i in range(total)],
      "rigGroup":base+"_SplineRig","visibleGroup":base+"_SplineRigVisible","hiddenGroup":base+"_SplineRigHidden",
      "globalGroup":base+"_SplineControls_GlobalGrp","base":base}

def _match_group(cmds,node,name):
    grp=cmds.group(empty=True,name=name); cmds.matchTransform(grp,node); return grp

def apply_spline_control_from_objs(data):
    import maya.cmds as cmds
    p=normalize_spline_control_from_objs(data)
    missing=[x for x in [p["parent"],p["parentGlobal"],p["curve"]]+p["joints"] if not cmds.objExists(x)]
    if missing: raise ValueError("Missing spline control objects: "+", ".join(missing))
    if not cmds.objExists(p["rigGroup"]): cmds.group(empty=True,name=p["rigGroup"],parent=p["parent"])
    if not cmds.objExists(p["visibleGroup"]): cmds.group(empty=True,name=p["visibleGroup"],parent=p["rigGroup"])
    if not cmds.objExists(p["hiddenGroup"]): cmds.group(empty=True,name=p["hiddenGroup"],parent=p["rigGroup"])
    cmds.setAttr(p["hiddenGroup"]+".visibility",0)
    control_joints=[]
    for i,u in enumerate(p["parameters"]):
        poc=cmds.createNode("pointOnCurveInfo"); cmds.connectAttr(p["curve"]+".worldSpace[0]",poc+".inputCurve",force=True)
        cmds.setAttr(poc+".turnOnPercentage",1); cmds.setAttr(poc+".parameter",u); pos=cmds.getAttr(poc+".position")[0]; cmds.delete(poc)
        cmds.select(clear=True); control_joints.append(cmds.joint(position=pos,name="%s_CtrlJnt_%02d"%(p["base"],i+1)))
    skin=cmds.skinCluster(control_joints,p["curve"],toSelectedBones=True,maximumInfluences=2)[0]
    spline_ctrls=[]; zeros=[]; size=cmds.arclen(p["curve"])*0.03
    for jnt in control_joints:
        ctrl=cmds.curve(degree=1,point=[(-1,0,-1),(-1,0,1),(1,0,1),(1,0,-1),(-1,0,-1)],name=jnt.replace("_CtrlJnt","_Ctrl"))
        cmds.scale(size,size,size,ctrl); cmds.makeIdentity(ctrl,apply=True)
        zero=cmds.group(ctrl,name=ctrl+"_Zero"); cmds.xform(zero,worldSpace=True,matrix=cmds.xform(jnt,query=True,worldSpace=True,matrix=True))
        cmds.parentConstraint(ctrl,jnt,maintainOffset=False); spline_ctrls.append(ctrl); zeros.append(zero)
    global_grp=_match_group(cmds,spline_ctrls[0],p["globalGroup"]); cmds.parent(global_grp,p["visibleGroup"]); cmds.parent(zeros,global_grp)
    cmds.parent(p["curve"],p["joints"][0],control_joints,p["hiddenGroup"])
    master=spline_ctrls[0]
    if not cmds.attributeQuery("Global",node=master,exists=True): cmds.addAttr(master,longName="Global",attributeType="double",minValue=0,maxValue=1,defaultValue=0,keyable=True)
    blend=cmds.shadingNode("blendColors",asUtility=True)
    parent_con=cmds.parentConstraint(p["parentGlobal"],global_grp,maintainOffset=True)[0]; cmds.setAttr(parent_con+".interpType",2)
    for a in ("rx","ry","rz"):
        for src in cmds.listConnections(global_grp+"."+a,source=True,destination=False,plugs=True) or []: cmds.disconnectAttr(src,global_grp+"."+a)
    orient_con=cmds.orientConstraint(p["parent"],global_grp,maintainOffset=True)[0]
    for a in ("rx","ry","rz"):
        for src in cmds.listConnections(global_grp+"."+a,source=True,destination=False,plugs=True) or []: cmds.disconnectAttr(src,global_grp+"."+a)
    cmds.connectAttr(parent_con+".constraintRotate",blend+".color1",force=True); cmds.connectAttr(orient_con+".constraintRotate",blend+".color2",force=True)
    cmds.connectAttr(blend+".output",global_grp+".rotate",force=True); cmds.connectAttr(master+".Global",blend+".blender",force=True)
    return {"plan":p,"controlJoints":control_joints,"splineControls":spline_ctrls,"skinCluster":skin,"globalGroup":global_grp,"parentConstraint":parent_con,"orientConstraint":orient_con,"blend":blend}

def spline_control_from_objs_managed_maya_smoke():
    import maya.cmds as cmds
    parent=cmds.createNode("transform",name="AIBridgeSplineControlParent"); world=cmds.createNode("transform",name="AIBridgeSplineControlWorld")
    cmds.select(clear=True); joints=[]
    for i,x in enumerate((0.0,5.0,10.0)):
        j=cmds.joint(position=(x,0,0),name="AIBridgeSplineControl%d_SplineJnt"%(i+1)); joints.append(j)
    curve=cmds.curve(degree=2,point=[(0,0,0),(5,0,0),(10,0,0)],name="AIBridgeSplineControlCurve")
    r=apply_spline_control_from_objs({"parent":parent,"parentGlobal":world,"curve":curve,"joints":joints,"numberCtrls":1})
    checks={"controls":len(r["splineControls"])==3,"controlJoints":len(r["controlJoints"])==3,"global":cmds.attributeQuery("Global",node=r["splineControls"][0],exists=True),"skin":cmds.objExists(r["skinCluster"])}
    if not all(checks.values()): raise RuntimeError("SplineControlFromObjs smoke failed: {0}".format(checks))
    return {"ok":True,"checks":checks}
