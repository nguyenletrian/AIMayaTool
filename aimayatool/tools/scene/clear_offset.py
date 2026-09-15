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
        parent=parents[0] if parents else None
        group=cmds.group(empty=True,name=name)
        cmds.delete(cmds.parentConstraint(obj,group,maintainOffset=False))
        if parent: group=cmds.parent(group,parent)[0]
        child=cmds.parent(obj,group)[0]
        results.append({"object":obj,"status":"applied","group":group,"child_path":child,"original_parent":parent})
    return tuple(results)


def clear_offset_items(items,cmds_module=None): return execute_clear_offset_plan(build_clear_offset_plan(items),cmds_module=cmds_module)


def apply_clear_offset(objects,suffix="_ClearOffsetGrp"):
    # Compatibility entry point. Exact legacy behavior uses _ClearOffsetGrp.
    if suffix=="_ClearOffsetGrp": return clear_offset_items([{"objects":tuple(objects or ())}])
    plan=tuple({"object":obj,"group_name":obj+suffix} for obj in tuple(objects or ()))
    return execute_clear_offset_plan(plan)
