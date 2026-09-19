from __future__ import absolute_import
import copy

def _lines(value):
    if isinstance(value,(list,tuple)): items=value
    else: items=str(value or "").splitlines()
    return [str(x).strip() for x in items if str(x).strip()]

def normalize_ikfk_snap_item(data):
    data=dict(data or {})
    item={"controlParent":str(data.get("controlParent","")).strip(),"switchControl":str(data.get("switchControl","")).strip(),
          "switchAttr":str(data.get("switchAttr","")).strip(),"valueActive":int(data.get("valueActive",0)),
          "refObjects":_lines(data.get("refObjects")),"sources":_lines(data.get("sources")),"targets":_lines(data.get("targets")),
          "mirror":bool(data.get("mirror",False))}
    if not item["switchControl"] or not item["switchAttr"]: raise ValueError("switchControl and switchAttr are required")
    if not item["sources"] or len(item["sources"])!=len(item["targets"]): raise ValueError("sources and targets must be non-empty and paired")
    return item

def mirror_ikfk_snap_item(item, mirror_name):
    out=copy.deepcopy(normalize_ikfk_snap_item(item))
    for key in ("switchControl","refObjects","sources","targets"):
        value=out[key]
        out[key]=[mirror_name(x) for x in value] if isinstance(value,list) else mirror_name(value)
    out["mirror"]=False
    return out

def expand_ikfk_snap_items(items, mirror_name=None):
    result=[]
    for raw in items or []:
        item=normalize_ikfk_snap_item(raw); result.append(item)
        if item["mirror"]:
            if mirror_name is None: raise ValueError("mirror_name is required when mirror is enabled")
            result.append(mirror_ikfk_snap_item(item,mirror_name))
    return result

def build_ikfk_snap_plan(items, mirror_name=None, add_keys=False):
    expanded=expand_ikfk_snap_items(items,mirror_name)
    return {"version":1,"items":expanded,"rigUI":"Rig_UI","dataNode":"NLTA_DataNode","dataAttribute":"IKFKData",
            "matrixAttributes":[s+"_Matrix" for i in expanded for s in i["sources"]],
            "keyAttributes":["tx","ty","tz","rx","ry","rz"] if add_keys else []}
