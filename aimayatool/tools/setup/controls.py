from __future__ import absolute_import

_SHAPES = {"circle": [(1.0,0.0,0.0),(0.707,0.0,0.707),(0.0,0.0,1.0),(-0.707,0.0,0.707),(-1.0,0.0,0.0),(-0.707,0.0,-0.707),(0.0,0.0,-1.0),(0.707,0.0,-0.707),(1.0,0.0,0.0)], "box": [(-1,-1,-1),(-1,-1,1),(-1,1,1),(-1,1,-1),(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1),(1,1,1),(1,1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1)]}
_SHAPE_ALIASES = {"cube":"box"}
def _cmds(): import maya.cmds as cmds; return cmds
def available_shapes(): return tuple(sorted(set(_SHAPES)|set(_SHAPE_ALIASES)))
def _canonical_shape(shape): return _SHAPE_ALIASES.get(shape,shape)
def _scaled_points(shape,size):
    shape=_canonical_shape(shape)
    if shape not in _SHAPES: raise ValueError("Unsupported control shape: {0}".format(shape))
    size=float(size)
    if size<=0: raise ValueError("Control size must be greater than zero.")
    return [(x*size,y*size,z*size) for x,y,z in _SHAPES[shape]]
def normalize_curve_shape_data(data):
    if not isinstance(data,dict): raise TypeError("Curve shape data must be a dictionary")
    degree=int(data.get("degree",1)); form=int(data.get("form",0))
    if degree<1: raise ValueError("Curve degree must be at least 1.")
    raw=data.get("points",data.get("pointData",[]))
    if isinstance(raw,dict):
        def key(item):
            digits="".join(c for c in str(item[0]) if c.isdigit()); return int(digits) if digits else str(item[0])
        raw=[value for _,value in sorted(raw.items(),key=key)]
    points=tuple(tuple(float(v) for v in p) for p in (raw or []))
    if any(len(p)!=3 for p in points): raise ValueError("Curve points must contain XYZ triples.")
    if len(points)<degree+1: raise ValueError("Curve data does not contain enough points for its degree.")
    result={"degree":degree,"form":form,"points":points}
    if data.get("knots") is not None: result["knots"]=tuple(float(v) for v in data["knots"])
    return result
def build_curve_create_kwargs(data):
    """Build deterministic maya.cmds.curve kwargs from normalized serialized AS data."""
    spec=normalize_curve_shape_data(data); kwargs={"degree":spec["degree"],"point":list(spec["points"])}
    if "knots" in spec: kwargs["knot"]=list(spec["knots"])
    if spec["form"] not in (0,1,2): raise ValueError("Unsupported curve form: {0}".format(spec["form"]))
    kwargs["periodic"]=spec["form"]==2
    return kwargs
def create_curve_from_shape_data(data,name=None,cmds_module=None):
    """Reconstruct one serialized curve through an injectable Maya command boundary."""
    cmds=cmds_module or _cmds(); kwargs=build_curve_create_kwargs(data)
    if name: kwargs["name"]=name
    return cmds.curve(**kwargs)
def create_control(name,shape="circle",size=1.0,match=None,parent=None):
    cmds=_cmds(); control=cmds.curve(name=name,degree=1,point=_scaled_points(shape,size))
    if match: cmds.xform(control,worldSpace=True,matrix=cmds.xform(match,query=True,worldSpace=True,matrix=True))
    if parent: cmds.parent(control,parent)
    return control
def replace_control_shape(node,shape="circle",size=1.0):
    cmds=_cmds(); shapes=cmds.listRelatives(node,shapes=True,type="nurbsCurve",fullPath=True) or []
    if not shapes: raise ValueError("Control has no nurbsCurve shape: {0}".format(node))
    old=shapes[0]; old_short=old.split("|")[-1]; cmds.delete(old); temp=cmds.curve(name=node.split("|")[-1]+"_shapeTmp",degree=1,point=_scaled_points(shape,size)); temp_shape=cmds.listRelatives(temp,shapes=True,type="nurbsCurve",fullPath=True)[0]; new=cmds.parent(temp_shape,node,shape=True,relative=True)[0]; cmds.delete(temp); return node,cmds.rename(new,old_short)
def create_zero_group(node,suffix="_ZERO"):
    cmds=_cmds(); matrix=cmds.xform(node,query=True,worldSpace=True,matrix=True); group=cmds.createNode("transform",name=node.split("|")[-1]+suffix); cmds.xform(group,worldSpace=True,matrix=matrix); return group,cmds.parent(node,group)[0]
def create_controls_for_nodes(nodes,shape="circle",size=1.0,suffix="_CTRL"): return [create_control(n.split("|")[-1]+suffix,shape,size,match=n) for n in nodes]
