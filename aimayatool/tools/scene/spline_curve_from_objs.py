from __future__ import absolute_import

def _names(value):
    if isinstance(value, str): value=value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]

def normalize_spline_curve_from_objs(data):
    data=data or {}
    parent=str(data.get("parent","")).strip()
    controls=_names(data.get("controls"))
    rebuild=int(data.get("rebuild",100))
    if not parent: raise ValueError("parent must not be empty")
    if len(controls)<2: raise ValueError("controls must contain at least two controls")
    if rebuild<1: raise ValueError("rebuild must be at least 1")
    root=controls[0]
    return {"parent":parent,"controls":controls,"rebuild":rebuild,
            "offsetGroups":[x+"_SplineOffset" for x in controls],
            "joints":[x+"_SplineJnt" for x in controls],
            "followGroups":[x+"_SplineRef" for x in controls],
            "curve":root+"_SplineJnt_SplineCurve",
            "rebuiltCurve":root+"_SplineJnt_SplineCurve_Rebuild",
            "rigGroup":root+"_SplineRig","visibleGroup":root+"_SplineRigVisible",
            "hiddenGroup":root+"_SplineRigHidden"}

def _match_group(cmds,node,name):
    grp=cmds.group(empty=True,name=name); cmds.matchTransform(grp,node); return grp

def _offset_group(cmds,node,name):
    parent=(cmds.listRelatives(node,parent=True,fullPath=True) or [None])[0]
    grp=_match_group(cmds,node,name)
    if parent: cmds.parent(grp,parent)
    cmds.parent(node,grp); return grp

def _apply_spline_curve_from_objs_unprotected(data):
    import maya.cmds as cmds
    plan=normalize_spline_curve_from_objs(data)
    missing=[x for x in [plan["parent"]]+plan["controls"] if not cmds.objExists(x)]
    if missing: raise ValueError("Missing spline curve objects: "+", ".join(missing))
    for ctrl,offset in zip(plan["controls"],plan["offsetGroups"]):
        if not cmds.objExists(offset): _offset_group(cmds,ctrl,offset)
    joints=[]
    for ctrl,name in zip(plan["controls"],plan["joints"]):
        cmds.select(clear=True)
        joints.append(cmds.joint(position=cmds.xform(ctrl,query=True,worldSpace=True,translation=True),name=name))
    for i in range(1,len(joints)): cmds.parent(joints[i],joints[i-1])
    cmds.joint(joints[0],edit=True,orientJoint="xyz",secondaryAxisOrient="yup",children=True,zeroScaleOrient=True)
    cmds.joint(joints[-1],edit=True,orientJoint="none")
    refs=[]
    for ctrl,jnt,name in zip(plan["controls"],joints,plan["followGroups"]):
        grp=_match_group(cmds,ctrl,name); cmds.parent(grp,jnt); refs.append(grp)
    points=[cmds.xform(j,query=True,worldSpace=True,translation=True) for j in joints]
    curve=cmds.curve(degree=min(3,len(points)-1),point=points,name=plan["curve"])
    rebuilt=cmds.rebuildCurve(curve,constructionHistory=True,replaceOriginal=False,rebuildType=0,endKnots=True,keepRange=False,keepControlPoints=False,keepEndPoints=True,keepTangents=False,spans=plan["rebuild"],degree=3,tolerance=0.01)[0]
    rebuilt=cmds.rename(rebuilt,plan["rebuiltCurve"])
    cmds.setAttr(curve+".inheritsTransform",0); cmds.setAttr(rebuilt+".inheritsTransform",0)
    ik=cmds.ikHandle(startJoint=joints[0],endEffector=joints[-1],solver="ikSplineSolver",curve=rebuilt,createCurve=False,parentCurve=False)[0]
    rig=cmds.group(empty=True,name=plan["rigGroup"])
    visible=cmds.group(empty=True,name=plan["visibleGroup"],parent=rig)
    hidden=cmds.group(empty=True,name=plan["hiddenGroup"],parent=rig); cmds.setAttr(hidden+".visibility",0)
    cmds.parent(curve,ik,joints[0],rebuilt,hidden); cmds.parent(rig,plan["parent"])
    return {"plan":plan,"joints":joints,"followGroups":refs,"curve":curve,"rebuiltCurve":rebuilt,"ikHandle":ik,"rigGroup":rig,"visibleGroup":visible,"hiddenGroup":hidden}


def apply_spline_curve_from_objs(data):
    import maya.cmds as cmds
    selection_uuids=cmds.ls(selection=True,uuid=True) or []
    try:
        return _apply_spline_curve_from_objs_unprotected(data)
    finally:
        restored=[]
        for node_uuid in selection_uuids:
            matches=cmds.ls(node_uuid,long=True) or []
            if matches:
                restored.append(matches[0])
        if restored:
            cmds.select(restored,replace=True)
        else:
            cmds.select(clear=True)

def spline_curve_from_objs_managed_maya_smoke():
    import maya.cmds as cmds
    parent=cmds.createNode("transform",name="AIBridgeSplineCurveParent")
    controls=[]
    for i,x in enumerate((0.0,5.0,10.0)):
        c=cmds.createNode("transform",name="AIBridgeSplineCurveCtrl%d"%(i+1)); cmds.setAttr(c+".tx",x); controls.append(c)
    result=apply_spline_curve_from_objs({"parent":parent,"controls":controls,"rebuild":8})
    checks={"curve":cmds.objExists(result["curve"]),"rebuilt":cmds.objExists(result["rebuiltCurve"]),"ik":cmds.objExists(result["ikHandle"]),"joints":len(result["joints"])==3,"refs":len(result["followGroups"])==3}
    if not all(checks.values()): raise RuntimeError("SplineCurveFromObjs smoke failed: {0}".format(checks))
    return {"ok":True,"checks":checks}

def spline_curve_from_objs_selection_state_managed_maya_smoke():
    """Measure whether Spline Curve From Objects preserves unrelated selection."""
    import maya.cmds as cmds
    parent=cmds.createNode("transform",name="AIBridgeSplineCurveStateParent")
    controls=[]
    for i,x in enumerate((0.0,5.0,10.0)):
        c=cmds.createNode("transform",name="AIBridgeSplineCurveStateCtrl%d"%(i+1))
        cmds.setAttr(c+".tx",x)
        controls.append(c)
    sentinel=cmds.createNode("transform",name="AIBridgeSplineCurveStateSentinel")
    cmds.select(sentinel,replace=True)
    before=cmds.ls(selection=True,long=True) or []
    result=apply_spline_curve_from_objs({"parent":parent,"controls":controls,"rebuild":8})
    after=cmds.ls(selection=True,long=True) or []
    functional=bool(
        cmds.objExists(result["curve"])
        and cmds.objExists(result["rebuiltCurve"])
        and cmds.objExists(result["ikHandle"])
        and len(result["joints"])==3
        and len(result["followGroups"])==3
    )
    return {
        "operation":"spline_curve_from_objs_selection_state",
        "functional":functional,
        "selection_preserved":before==after,
        "before":before,
        "after":after,
    }

