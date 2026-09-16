"""ScenePattern CreateOffset composition over the shared Setup offset primitive."""
from __future__ import absolute_import


def normalize_create_offset_item(item):
    if not isinstance(item, dict): raise TypeError("CreateOffset item must be a dictionary")
    objects=item.get("objects",())
    if isinstance(objects,str): objects=objects.splitlines()
    objects=tuple(str(node).strip() for node in (objects or ()) if str(node).strip())
    extra_name=str(item.get("extraName") or item.get("suffix") or "").strip()
    return {"objects":objects,"extra_name":extra_name}


def build_create_offset_plan(items):
    if items is None: return tuple()
    if not isinstance(items,(list,tuple)): raise TypeError("CreateOffset items must be a list or tuple")
    plan=[]
    for item in items:
        data=normalize_create_offset_item(item)
        for node in data["objects"]: plan.append({"object":node,"group_name":node+(data["extra_name"] or "ExtraName")})
    return tuple(plan)


def execute_create_offset_plan(plan,insert_offset_group_fn=None,exists_fn=None):
    if insert_offset_group_fn is None:
        from aimayatool.tools.setup.transforms import insert_offset_group
        insert_offset_group_fn=insert_offset_group
    if exists_fn is None:
        import maya.cmds as cmds
        exists_fn=cmds.objExists
    results=[]
    for entry in tuple(plan or ()):
        node,group_name=entry["object"],entry["group_name"]
        if not node or not exists_fn(node): results.append({"object":node,"status":"skipped_missing"}); continue
        result=insert_offset_group_fn(node,name=group_name); results.append({"object":node,"status":"applied","group":result["group"],"node":result["node"],"group_name":group_name})
    return tuple(results)


def create_offsets(items,insert_offset_group_fn=None,exists_fn=None): return execute_create_offset_plan(build_create_offset_plan(items),insert_offset_group_fn=insert_offset_group_fn,exists_fn=exists_fn)
def apply_create_offset(objects,extra_name=""): return create_offsets([{"objects":tuple(objects or ()),"extraName":extra_name}])
def _matrix_close(a,b,tolerance=1e-9): return len(a)==len(b) and all(abs(float(x)-float(y))<=tolerance for x,y in zip(a,b))


def create_offset_managed_maya_smoke():
    import maya.cmds as cmds
    cmds.file(new=True,force=True)
    parent=cmds.group(empty=True,name="Rig_GRP"); cmds.xform(parent,translation=(7,-3,2),rotation=(13,27,-9),scale=(1.2,0.9,1.1))
    first=cmds.group(empty=True,name="First_CTRL",parent=parent); second=cmds.group(empty=True,name="Second_CTRL",parent=parent)
    cmds.xform(first,translation=(1,2,3),rotation=(10,20,30)); cmds.xform(second,translation=(-2,1,4),rotation=(-10,5,15))
    before={node:tuple(cmds.xform(node,query=True,worldSpace=True,matrix=True)) for node in (first,second)}
    applied=apply_create_offset((first,second),"_SceneOffset"); named=all(item["status"]=="applied" and cmds.objExists(item["group_name"]) for item in applied)
    after={node:tuple(cmds.xform(node,query=True,worldSpace=True,matrix=True)) for node in (first,second)}; preserved=all(_matrix_close(after[node],before[node]) for node in (first,second)); max_delta=max(abs(float(x)-float(y)) for node in (first,second) for x,y in zip(after[node],before[node]))
    third=cmds.group(empty=True,name="Third_CTRL",parent=parent); fallback=apply_create_offset((third,),"")[0]; fallback_ok=fallback["status"]=="applied" and fallback["group_name"]=="Third_CTRLExtraName" and cmds.objExists("Third_CTRLExtraName")
    missing=apply_create_offset(("Missing_CTRL",),"_SceneOffset")[0]; missing_ok=missing["status"]=="skipped_missing"
    smoke={"named":named,"world_matrix_preserved":preserved,"max_matrix_delta":max_delta,"fallback":fallback_ok,"missing":missing_ok,"success":bool(named and preserved and fallback_ok and missing_ok)}
    if not smoke["success"]: raise AssertionError("CreateOffset managed Maya smoke failed: %r" % smoke)
    return smoke
