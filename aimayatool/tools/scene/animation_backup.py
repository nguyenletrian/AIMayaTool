from __future__ import absolute_import

import json


def normalize_animation_backup_data(data):
    if data is None: return {}
    if not isinstance(data,dict): raise TypeError("AnimationBackup data must be a dictionary.")
    result={}
    for obj,attrs in data.items():
        if not isinstance(attrs,dict): continue
        normalized={}
        for attr,curve in attrs.items():
            if not isinstance(curve,dict): continue
            times=tuple(float(v) for v in (curve.get("times") or ())); values=tuple(float(v) for v in (curve.get("values") or ()))
            if len(times)!=len(values): raise ValueError("Animation backup times/values length mismatch: {0}.{1}".format(obj,attr))
            if times: normalized[str(attr)]={"times":times,"values":values}
        if normalized: result[str(obj)]=normalized
    return result


def build_animation_apply_plan(data):
    normalized=normalize_animation_backup_data(data); plan=[]
    for obj in sorted(normalized):
        for attr in sorted(normalized[obj]):
            curve=normalized[obj][attr]; plan.append({"object":obj,"attribute":attr,"plug":obj+"."+attr,"keys":tuple(zip(curve["times"],curve["values"]))})
    return tuple(plan)


def collect_animation_data(objects,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    data={}
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj): continue
        long_names=cmds.ls(obj,long=True) or [obj]; long_name=long_names[0]; obj_data={}
        for attr in cmds.listAttr(long_name,keyable=True) or []:
            plug=long_name+"."+attr; curves=cmds.listConnections(plug,source=True,destination=False,type="animCurve") or []
            if not curves: continue
            curve=curves[0]; times=cmds.keyframe(curve,query=True,timeChange=True) or []; values=cmds.keyframe(curve,query=True,valueChange=True) or []
            if times: obj_data[attr]={"times":times,"values":values}
        if obj_data: data[obj]=obj_data
    return normalize_animation_backup_data(data)


def write_animation_backup(path,objects,cmds_module=None):
    data=collect_animation_data(objects,cmds_module=cmds_module)
    with open(path,"w") as stream: json.dump(data,stream,indent=2,sort_keys=True)
    return data


def read_animation_backup(path):
    with open(path,"r") as stream: data=json.load(stream)
    return normalize_animation_backup_data(data)


def execute_animation_apply_plan(plan,cmds_module=None,clear_existing=True):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    results=[]
    for entry in tuple(plan or ()):
        obj,plug=entry["object"],entry["plug"]
        if not cmds.objExists(obj) or not cmds.objExists(plug): results.append({"plug":plug,"status":"skipped_missing"}); continue
        if clear_existing: cmds.cutKey(plug,clear=True)
        for time,value in entry["keys"]: cmds.setKeyframe(plug,time=time,value=value)
        results.append({"plug":plug,"status":"applied","key_count":len(entry["keys"])})
    return tuple(results)


def apply_animation_data(data,clear_existing=True,cmds_module=None): return execute_animation_apply_plan(build_animation_apply_plan(data),cmds_module=cmds_module,clear_existing=clear_existing)
def import_animation_backup(path,clear_existing=True,cmds_module=None): return apply_animation_data(read_animation_backup(path),clear_existing=clear_existing,cmds_module=cmds_module)
