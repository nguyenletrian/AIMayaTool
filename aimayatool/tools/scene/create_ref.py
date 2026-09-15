from __future__ import absolute_import


def normalize_create_ref_item(item):
    if not isinstance(item, dict): raise TypeError("CreateRef item must be a dictionary.")
    objects=item.get("objects",())
    if isinstance(objects,str): objects=objects.splitlines()
    return {"objects":tuple(str(obj).strip() for obj in (objects or ()) if str(obj).strip()),"parent":str(item.get("parent","")).strip() or None}


def build_create_ref_plan(items):
    if items is None: return tuple()
    if not isinstance(items,(list,tuple)): raise TypeError("CreateRef items must be a list or tuple.")
    plan=[]
    for item in items:
        data=normalize_create_ref_item(item)
        for obj in data["objects"]: plan.append({"object":obj,"reference_name":obj+"_Ref","parent":data["parent"]})
    return tuple(plan)


def execute_create_ref_plan(plan,cmds_module=None):
    if cmds_module is None:
        import maya.cmds as cmds
    else: cmds=cmds_module
    results=[]
    for entry in tuple(plan or ()):
        obj,name,parent=entry["object"],entry["reference_name"],entry["parent"]
        if not cmds.objExists(obj): results.append({"object":obj,"status":"skipped_missing"}); continue
        if parent and not cmds.objExists(parent): raise ValueError("Parent does not exist: {0}".format(parent))
        if cmds.objExists(name): results.append({"object":obj,"status":"skipped_existing","reference":name}); continue
        ref=cmds.group(empty=True,name=name); cmds.matchTransform(ref,obj)
        if parent: ref=cmds.parent(ref,parent)[0]
        results.append({"object":obj,"status":"created","reference":ref})
    return tuple(results)


def create_ref_items(items,cmds_module=None): return execute_create_ref_plan(build_create_ref_plan(items),cmds_module=cmds_module)


def create_references(objects,parent=None,suffix="_Ref"):
    # Compatibility entry point. Legacy ScenePattern CreateRef always uses _Ref.
    if suffix!="_Ref":
        items=[{"objects":tuple(objects or ()),"parent":parent}]
        plan=tuple({"object":entry["object"],"reference_name":entry["object"]+suffix,"parent":entry["parent"]} for entry in build_create_ref_plan(items))
        return execute_create_ref_plan(plan)
    return create_ref_items([{"objects":tuple(objects or ()),"parent":parent}])
