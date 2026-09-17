from __future__ import absolute_import

from aimayatool.tools.setup import controls

_AXIS_MAP={"x":(1.0,0.0,0.0),"-x":(-1.0,0.0,0.0),"y":(0.0,1.0,0.0),"-y":(0.0,-1.0,0.0),"z":(0.0,0.0,1.0),"-z":(0.0,0.0,-1.0)}


def axis_vector(axis):
    key=str(axis or "").strip().lower()
    if key not in _AXIS_MAP: raise ValueError("Unsupported aim axis: {0}".format(axis))
    return _AXIS_MAP[key]


def build_aim_constraint_plan(descriptor):
    data=dict(descriptor or {}); child=str(data.get("child") or "").strip(); parent=str(data.get("parent") or "").strip(); reference=str(data.get("reference") or "").strip()
    if not child or not parent or not reference: raise ValueError("Aim Constraint requires child, parent and reference.")
    return ({"operation":"aim_constraint","child":child,"parent":parent,"reference":reference,"offset_name":child+"_AimGrp","aim_vector":axis_vector(data.get("mainAxis","x")),"up_vector":axis_vector(data.get("secondAxis","y")),"maintain_offset":bool(data.get("maintain",True)),"constraint_content":str(data.get("constraintContent") or "").strip()},)


def execute_aim_constraint_plan(plan,cmds_module=None,create_offset_fn=None):
    if cmds_module is None:
        import maya.cmds as cmds
    else: cmds=cmds_module
    if create_offset_fn is None: create_offset_fn=lambda child,name: controls.create_zero_group(child,suffix=name[len(child):])
    results=[]
    for operation in tuple(plan or ()):
        if operation.get("operation")!="aim_constraint": raise ValueError("Unsupported Aim Constraint operation: {0}".format(operation.get("operation")))
        child=operation["child"]
        if not cmds.objExists(child): results.append({"child":child,"status":"skipped_missing_child"}); continue
        for key in ("parent","reference"):
            node=operation[key]
            if not cmds.objExists(node): raise ValueError("Aim Constraint {0} does not exist: {1}".format(key,node))
        content=operation.get("constraint_content") or ""
        if content and not cmds.objExists(content): raise ValueError("Aim Constraint constraint_content does not exist: {0}".format(content))
        offset,child_path=create_offset_fn(child,operation.get("offset_name") or child+"_AimGrp")
        constraint=cmds.aimConstraint(operation["parent"],offset,aimVector=tuple(operation["aim_vector"]),upVector=tuple(operation["up_vector"]),worldUpType="object",worldUpObject=operation["reference"],mo=bool(operation.get("maintain_offset",True)))[0]
        if content: constraint=cmds.parent(constraint,content)[0]
        results.append({"child":child,"child_path":child_path,"status":"applied","offset":offset,"constraint":constraint})
    return tuple(results)


def apply_aim_constraint(descriptor,cmds_module=None,create_offset_fn=None): return execute_aim_constraint_plan(build_aim_constraint_plan(descriptor),cmds_module=cmds_module,create_offset_fn=create_offset_fn)


def aim_constraint_managed_maya_smoke():
    import maya.cmds as cmds
    cmds.file(new=True,force=True)
    rig=cmds.group(empty=True,name="Rig_GRP"); child=cmds.group(empty=True,name="Aim_CTRL",parent=rig); target=cmds.group(empty=True,name="Aim_Target",parent=rig); reference=cmds.group(empty=True,name="Aim_Up",parent=rig); content=cmds.group(empty=True,name="ConstraintContent_GRP")
    cmds.xform(child,translation=(1.0,2.0,0.0)); cmds.xform(target,translation=(8.0,3.0,1.0)); cmds.xform(reference,translation=(1.0,7.0,2.0))
    result=apply_aim_constraint({"child":child,"parent":target,"reference":reference,"mainAxis":"x","secondAxis":"y","maintain":False,"constraintContent":content})[0]
    constraint=result.get("constraint"); offset=result.get("offset"); applied=result.get("status")=="applied" and cmds.objExists(offset) and cmds.objExists(constraint)
    hierarchy=bool(applied and (cmds.listRelatives(child,parent=True,fullPath=False) or [None])[0].split("|")[-1]==offset.split("|")[-1])
    constraint_parent=(cmds.listRelatives(constraint,parent=True,fullPath=False) or [None])[0] if applied else None; content_ok=bool(constraint_parent and constraint_parent.split("|")[-1]==content)
    target_ok=bool(applied and target in (cmds.aimConstraint(constraint,query=True,targetList=True) or [])); world_up_ok=bool(applied and cmds.getAttr(constraint+".worldUpType")==1 and cmds.listConnections(constraint+".worldUpMatrix",source=True,destination=False))
    missing=apply_aim_constraint({"child":"Missing_CTRL","parent":target,"reference":reference})[0]; missing_ok=missing.get("status")=="skipped_missing_child"
    invalid_parent=False
    try: apply_aim_constraint({"child":child,"parent":"Missing_Target","reference":reference})
    except ValueError: invalid_parent=True
    axis_ok=axis_vector("-z")== (0.0,0.0,-1.0)
    smoke={"applied":applied,"hierarchy":hierarchy,"constraint_content":content_ok,"target":target_ok,"world_up_object":world_up_ok,"missing_child":missing_ok,"invalid_parent":invalid_parent,"axis":axis_ok}
    smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError("AimConstraint managed Maya smoke failed: %r" % smoke)
    return smoke
