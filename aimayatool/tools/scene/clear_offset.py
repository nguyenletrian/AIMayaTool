from __future__ import absolute_import


def normalize_clear_offset_item(item):
    if not isinstance(item,dict): raise TypeError("ClearOffset item must be a dictionary.")
    objects=item.get("objects",())
    if isinstance(objects,str): objects=objects.splitlines()
    return tuple(str(obj).strip() for obj in (objects or ()) if str(obj).strip())


def build_clear_offset_plan(items):
    if items is None: return tuple()
    if not isinstance(items,(list,tuple)): raise TypeError("ClearOffset items must be a list or tuple.")
    return tuple({"object":obj,"group_name":obj+"_ClearOffsetGrp"} for item in items for obj in normalize_clear_offset_item(item))


def execute_clear_offset_plan(plan,cmds_module=None):
    if cmds_module is None:
        import maya.cmds as cmds
    else: cmds=cmds_module
    results=[]
    for entry in tuple(plan or ()):
        obj,name=entry["object"],entry["group_name"]
        if not obj or not cmds.objExists(obj): results.append({"object":obj,"status":"skipped_missing_object"}); continue
        parents=cmds.listRelatives(obj,parent=True,fullPath=True) or []
        if not parents: results.append({"object":obj,"status":"skipped_root_object"}); continue
        if cmds.objExists(name): results.append({"object":obj,"status":"skipped_name_collision","group_name":name}); continue
        parent=parents[0]
        group=cmds.group(empty=True,name=name)
        cmds.delete(cmds.parentConstraint(obj,group,maintainOffset=False))
        group=cmds.parent(group,parent)[0]
        child=cmds.parent(obj,group)[0]
        results.append({"object":obj,"status":"applied","group":group,"child_path":child,"original_parent":parent})
    return tuple(results)


def clear_offset_items(items,cmds_module=None): return execute_clear_offset_plan(build_clear_offset_plan(items),cmds_module=cmds_module)


def apply_clear_offset(objects,suffix="_ClearOffsetGrp"):
    # Compatibility entry point. Exact legacy behavior uses _ClearOffsetGrp.
    if suffix=="_ClearOffsetGrp": return clear_offset_items([{"objects":tuple(objects or ())}])
    plan=tuple({"object":obj,"group_name":obj+suffix} for obj in tuple(objects or ()))
    return execute_clear_offset_plan(plan)


def clear_offset_managed_maya_smoke():
    import maya.cmds as cmds
    cmds.file(new=True,force=True)
    rig=cmds.createNode("transform",name="Rig_GRP")
    arm=cmds.createNode("transform",name="arm_L",parent=rig)
    cmds.setAttr(arm+".translate",3.25,-1.5,7.0,type="double3")
    cmds.setAttr(arm+".rotate",18.0,-27.0,41.0,type="double3")
    before=cmds.xform(arm,query=True,matrix=True,worldSpace=True)
    applied=clear_offset_items([{"objects":[arm]}])
    after=cmds.xform(arm,query=True,matrix=True,worldSpace=True)
    group="arm_L_ClearOffsetGrp"
    matrix_ok=all(abs(a-b)<=1e-8 for a,b in zip(before,after))
    group_parent=cmds.listRelatives(group,parent=True,fullPath=False) or []
    arm_parent=cmds.listRelatives(arm,parent=True,fullPath=False) or []
    parented_ok=bool(applied and applied[0].get("status")=="applied" and cmds.objExists(group) and group_parent==[rig] and arm_parent==[group] and matrix_ok)

    root=cmds.createNode("transform",name="root_CTRL")
    root_result=clear_offset_items([{"objects":[root]}])
    root_ok=bool(root_result and root_result[0].get("status")=="skipped_root_object" and not cmds.objExists("root_CTRL_ClearOffsetGrp") and not (cmds.listRelatives(root,parent=True) or []))

    collision_parent=cmds.createNode("transform",name="CollisionRig_GRP")
    collision=cmds.createNode("transform",name="collision_CTRL",parent=collision_parent)
    cmds.createNode("transform",name="collision_CTRL_ClearOffsetGrp")
    collision_before=cmds.listRelatives(collision,parent=True,fullPath=False) or []
    collision_result=clear_offset_items([{"objects":[collision]}])
    collision_after=cmds.listRelatives(collision,parent=True,fullPath=False) or []
    collision_ok=bool(collision_result and collision_result[0].get("status")=="skipped_name_collision" and collision_before==collision_after==[collision_parent])

    result={"parented":{"ok":parented_ok,"status":applied[0].get("status") if applied else None,"matrix_preserved":matrix_ok},"root":{"ok":root_ok,"status":root_result[0].get("status") if root_result else None},"collision":{"ok":collision_ok,"status":collision_result[0].get("status") if collision_result else None}}
    result["success"]=all(section["ok"] for section in (result["parented"],result["root"],result["collision"]))
    if not result["success"]: raise AssertionError("ClearOffset managed Maya smoke failed: %r" % result)
    return result
