from __future__ import absolute_import


def build_orient_constraint_plan(items):
    if items is None: return tuple()
    if not isinstance(items,(list,tuple)): raise TypeError("OrientConstraint items must be a list or tuple")
    plan=[]
    for item in items:
        if not isinstance(item,dict): raise TypeError("OrientConstraint item must be a dictionary")
        parent=str(item.get("parent") or "").strip(); child=str(item.get("child") or "").strip(); container=str(item.get("constraintContent") or "").strip()
        if not parent or not child: raise ValueError("OrientConstraint requires parent and child.")
        plan.append({"parent":parent,"child":child,"maintain":bool(item.get("maintain",True)),"offset":bool(item.get("offset",True)),"constraint_content":container})
    return tuple(plan)


def execute_orient_constraint_plan(plan,create_fn=None,exists_fn=None):
    if create_fn is None:
        from aimayatool.tools.setup.constraints import create_orient_constraint
        create_fn=create_orient_constraint
    if exists_fn is None:
        import maya.cmds as cmds
        exists_fn=cmds.objExists
    results=[]
    for item in tuple(plan or ()):
        child=item["child"]
        if not exists_fn(child): results.append({"child":child,"status":"skipped_missing_child"}); continue
        if not exists_fn(item["parent"]): raise ValueError("OrientConstraint parent does not exist: {0}".format(item["parent"]))
        container=item.get("constraint_content") or None
        if container and not exists_fn(container): raise ValueError("OrientConstraint constraint_content does not exist: {0}".format(container))
        result=create_fn(item["parent"],child,maintain_offset=item["maintain"],use_offset_group=item["offset"],offset_suffix="_orientConstraintGrp",container=container)
        results.append({"child":child,"status":"applied","constraint":result["constraint"],"target":result["target"],"offset_group":result["offset_group"]})
    return tuple(results)


def create_orient_constraints(items): return execute_orient_constraint_plan(build_orient_constraint_plan(items))


def orient_constraint_managed_maya_smoke():
    import maya.cmds as cmds
    cmds.file(new=True,force=True)
    driver=cmds.group(empty=True,name="OrientDriver"); child=cmds.group(empty=True,name="OrientChild"); container=cmds.group(empty=True,name="ConstraintContent")
    cmds.xform(driver,rotation=(15,25,35)); cmds.xform(child,translation=(2,1,-3),rotation=(4,8,12))
    applied=create_orient_constraints([{"parent":driver,"child":child,"maintain":True,"offset":True,"constraintContent":container}])[0]
    offset=applied["offset_group"]; con=applied["constraint"]
    hierarchy=bool(offset and cmds.objExists(offset) and (cmds.listRelatives(child,parent=True) or [None])[0].split("|")[-1]==offset.split("|")[-1])
    con_parent=(cmds.listRelatives(con,parent=True) or [""])[0].split("|")[-1]; content_ok=con_parent==container
    targets=cmds.orientConstraint(con,query=True,targetList=True) or []; target_ok=bool(targets and targets[0].split("|")[-1]==driver)
    direct=cmds.group(empty=True,name="DirectChild"); direct_result=create_orient_constraints([{"parent":driver,"child":direct,"maintain":False,"offset":False}])[0]; no_offset=direct_result["offset_group"] is None and direct_result["target"]==direct
    missing=create_orient_constraints([{"parent":driver,"child":"MissingChild","offset":True}])[0]; missing_ok=missing["status"]=="skipped_missing_child"
    invalid=False
    try: create_orient_constraints([{"parent":"MissingParent","child":direct}])
    except ValueError: invalid=True
    smoke={"applied":applied["status"]=="applied","hierarchy":hierarchy,"constraint_content":content_ok,"target":target_ok,"no_offset":no_offset,"missing_child":missing_ok,"invalid_parent":invalid}
    smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError("OrientConstraint managed Maya smoke failed: %r" % smoke)
    return smoke
