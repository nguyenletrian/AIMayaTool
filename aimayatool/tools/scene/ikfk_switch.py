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


def _require_objects(cmds,names):
    missing=[n for n in names if not cmds.objExists(n)]
    if missing: raise ValueError("Missing IK/FK objects: "+", ".join(missing))

def capture_ikfk_offsets(item):
    import maya.cmds as cmds
    import maya.api.OpenMaya as om
    item=normalize_ikfk_snap_item(item)
    _require_objects(cmds,[item["switchControl"]]+item["sources"]+item["targets"])
    offsets={}
    for source,target in zip(item["sources"],item["targets"]):
        source_mtx=om.MMatrix(cmds.getAttr(source+".worldMatrix[0]"))
        target_mtx=om.MMatrix(cmds.getAttr(target+".worldMatrix[0]"))
        offsets[source]=list(source_mtx*target_mtx.inverse())
    return offsets

def apply_ikfk_snap(item,offsets,add_keys=False):
    import maya.cmds as cmds
    import maya.api.OpenMaya as om
    item=normalize_ikfk_snap_item(item)
    _require_objects(cmds,[item["switchControl"]]+item["sources"]+item["targets"])
    switch_plug=item["switchControl"]+"."+item["switchAttr"]
    if not cmds.objExists(switch_plug): raise ValueError("Missing IK/FK switch attribute: "+switch_plug)
    matrices={}
    for source,target in zip(item["sources"],item["targets"]):
        if source not in offsets: raise ValueError("Missing offset matrix for "+source)
        target_mtx=om.MMatrix(cmds.getAttr(target+".worldMatrix[0]"))
        matrices[source]=om.MMatrix(offsets[source])*target_mtx
    cmds.setAttr(switch_plug,item["valueActive"])
    if add_keys: cmds.setKeyframe(switch_plug)
    for source,matrix in matrices.items():
        cmds.xform(source,worldSpace=True,matrix=list(matrix))
        if add_keys: cmds.setKeyframe(source,attribute=["tx","ty","tz","rx","ry","rz"])
    return {"switchPlug":switch_plug,"valueActive":item["valueActive"],"sources":list(item["sources"]),"keyed":bool(add_keys)}

def ikfk_switch_managed_maya_smoke():
    import maya.cmds as cmds
    switch=cmds.createNode("transform",name="AIBridgeIKFKSwitch"); cmds.addAttr(switch,longName="blend",attributeType="double",keyable=True)
    source=cmds.createNode("transform",name="AIBridgeIKFKSource"); target=cmds.createNode("transform",name="AIBridgeIKFKTarget")
    cmds.setAttr(source+".tx",2); cmds.setAttr(target+".tx",5)
    item={"switchControl":switch,"switchAttr":"blend","valueActive":1,"sources":[source],"targets":[target],"refObjects":[]}
    offsets=capture_ikfk_offsets(item); cmds.setAttr(target+".tx",8); result=apply_ikfk_snap(item,offsets,add_keys=False)
    ok=abs(cmds.getAttr(source+".tx")-5.0)<0.001 and cmds.getAttr(switch+".blend")==1
    if not ok: raise RuntimeError("IK/FK switch smoke failed")
    return {"ok":True,"result":result}
