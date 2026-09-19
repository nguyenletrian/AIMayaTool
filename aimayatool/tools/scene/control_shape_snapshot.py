from __future__ import absolute_import

def _color(data):
    rgb=bool(data.get("overrideRGBColors",False))
    return {"overrideEnabled":bool(data.get("overrideEnabled",False)),"overrideRGBColors":rgb,
            "overrideColor":int(data.get("overrideColor",0)),
            "overrideColorRGB":[float(data.get("overrideColorR",0.0)),float(data.get("overrideColorG",0.0)),float(data.get("overrideColorB",0.0))]}

def normalize_curve_shape_snapshot(data):
    if not isinstance(data,dict): raise TypeError("Curve-shape snapshot must be a dictionary")
    out={"version":1,"controls":{}}
    for ctrl,raw in sorted(data.items()):
        if not isinstance(raw,dict): continue
        shapes={}
        for name,shape in sorted((raw.get("curveData") or {}).items()):
            points=shape.get("pointData") or {}
            shapes[str(name)]={"color":_color(shape),"visibility":bool(shape.get("visibility",True)),
                "points":{str(k):[float(x) for x in v] for k,v in sorted(points.items())}}
        out["controls"][str(ctrl)]={"color":_color(raw),"visibility":bool(raw.get("visibility",True)),"shapes":shapes}
    return out

def build_curve_shape_restore_plan(snapshot, existing=None):
    snap=normalize_curve_shape_snapshot(snapshot.get("controls",snapshot) if snapshot.get("version") else snapshot)
    existing=existing or {}
    plan=[]
    for ctrl,data in snap["controls"].items():
        current=existing.get(ctrl,{})
        for shape,sdata in data["shapes"].items():
            current_count=current.get(shape)
            plan.append({"control":ctrl,"shape":shape,"action":"update" if current_count==len(sdata["points"]) else "rebuild",
                         "points":sdata["points"],"color":sdata["color"],"visibility":sdata["visibility"]})
    return {"version":1,"controls":snap["controls"],"shapes":plan}


def capture_curve_shape_snapshot(controls=None):
    import maya.cmds as cmds
    controls=list(controls or cmds.ls(selection=True,type="transform") or [])
    data={}
    for ctrl in controls:
        if not cmds.objExists(ctrl): continue
        raw={"overrideEnabled":cmds.getAttr(ctrl+".overrideEnabled"),"overrideRGBColors":cmds.getAttr(ctrl+".overrideRGBColors"),
             "overrideColor":cmds.getAttr(ctrl+".overrideColor"),"visibility":cmds.getAttr(ctrl+".visibility"),"curveData":{}}
        try:
            rgb=cmds.getAttr(ctrl+".overrideColorRGB")[0]; raw.update({"overrideColorR":rgb[0],"overrideColorG":rgb[1],"overrideColorB":rgb[2]})
        except Exception: pass
        for shape in cmds.listRelatives(ctrl,shapes=True,type="nurbsCurve",fullPath=False) or []:
            path=ctrl+"|"+shape; s={"overrideEnabled":cmds.getAttr(path+".overrideEnabled"),"overrideRGBColors":cmds.getAttr(path+".overrideRGBColors"),
                "overrideColor":cmds.getAttr(path+".overrideColor"),"visibility":cmds.getAttr(path+".visibility"),"pointData":{}}
            try:
                rgb=cmds.getAttr(path+".overrideColorRGB")[0]; s.update({"overrideColorR":rgb[0],"overrideColorG":rgb[1],"overrideColorB":rgb[2]})
            except Exception: pass
            for cv in cmds.ls(path+".controlPoints[*]",flatten=True) or []:
                key=cv.rsplit(".",1)[-1]; s["pointData"][key]=cmds.xform(cv,query=True,objectSpace=True,translation=True)
            raw["curveData"][shape]=s
        data[ctrl]=raw
    return normalize_curve_shape_snapshot(data)

def _set_display(cmds,node,data):
    color=data["color"]; cmds.setAttr(node+".overrideEnabled",color["overrideEnabled"]); cmds.setAttr(node+".overrideRGBColors",color["overrideRGBColors"])
    cmds.setAttr(node+".visibility",data["visibility"])
    if color["overrideRGBColors"]: cmds.setAttr(node+".overrideColorRGB",*color["overrideColorRGB"])
    else: cmds.setAttr(node+".overrideColor",color["overrideColor"])

def apply_curve_shape_snapshot(snapshot,controls=None):
    import maya.cmds as cmds
    snap=normalize_curve_shape_snapshot(snapshot.get("controls",snapshot) if snapshot.get("version") else snapshot)
    selected=set(controls or snap["controls"].keys()); existing={}
    for ctrl in selected:
        if not cmds.objExists(ctrl): continue
        existing[ctrl]={}
        for shape in cmds.listRelatives(ctrl,shapes=True,type="nurbsCurve",fullPath=False) or []:
            existing[ctrl][shape]=len(cmds.ls(ctrl+"|"+shape+".controlPoints[*]",flatten=True) or [])
    plan=build_curve_shape_restore_plan(snap,existing)
    for ctrl,cdata in plan["controls"].items():
        if ctrl not in selected or not cmds.objExists(ctrl): continue
        _set_display(cmds,ctrl,cdata)
    for item in plan["shapes"]:
        ctrl=item["control"]
        if ctrl not in selected or not cmds.objExists(ctrl): continue
        path=ctrl+"|"+item["shape"]
        if item["action"]=="rebuild":
            if cmds.objExists(path): cmds.delete(path)
            points=[v for _,v in sorted(item["points"].items(),key=lambda kv:int(kv[0].split("[")[1].split("]")[0]))]
            degree=min(3,max(1,len(points)-1)); temp=cmds.curve(point=points,degree=degree)
            shape=(cmds.listRelatives(temp,shapes=True,fullPath=True) or [None])[0]
            if shape:
                shape=cmds.parent(shape,ctrl,shape=True,relative=True)[0]; shape=cmds.rename(shape,item["shape"]); path=ctrl+"|"+shape
            cmds.delete(temp)
        else:
            for key,value in item["points"].items(): cmds.xform(path+"."+key,objectSpace=True,translation=value)
        _set_display(cmds,path,{"color":item["color"],"visibility":item["visibility"]})
    return plan
