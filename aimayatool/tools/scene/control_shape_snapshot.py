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
