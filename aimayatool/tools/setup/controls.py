from __future__ import absolute_import


_SHAPES = {
    "circle": [(1.0, 0.0, 0.0), (0.707, 0.0, 0.707), (0.0, 0.0, 1.0), (-0.707, 0.0, 0.707), (-1.0, 0.0, 0.0), (-0.707, 0.0, -0.707), (0.0, 0.0, -1.0), (0.707, 0.0, -0.707), (1.0, 0.0, 0.0)],
    "box": [(-1.0,-1.0,-1.0),(-1.0,-1.0,1.0),(-1.0,1.0,1.0),(-1.0,1.0,-1.0),(-1.0,-1.0,-1.0),(1.0,-1.0,-1.0),(1.0,-1.0,1.0),(-1.0,-1.0,1.0),(1.0,-1.0,1.0),(1.0,1.0,1.0),(-1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,-1.0),(-1.0,1.0,-1.0),(1.0,1.0,-1.0),(1.0,-1.0,-1.0)],
    "sphere": [(0.0,1.0,0.0),(0.0,0.707,-0.707),(0.0,0.0,-1.0),(0.0,-0.707,-0.707),(0.0,-1.0,0.0),(0.0,-0.707,0.707),(0.0,0.0,1.0),(0.0,0.707,0.707),(0.0,1.0,0.0),(-0.707,0.707,0.0),(-1.0,0.0,0.0),(-0.707,-0.707,0.0),(0.0,-1.0,0.0),(0.707,-0.707,0.0),(1.0,0.0,0.0),(0.707,0.707,0.0),(0.0,1.0,0.0)],
    "diamond": [(0.0,0.0,0.866),(-0.866,0.0,0.0),(0.0,0.0,-0.866),(0.866,0.0,0.0),(0.0,0.0,0.866),(0.0,1.0,0.0),(-0.866,0.0,0.0),(0.0,-1.0,0.0),(0.866,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,-0.866),(0.0,-1.0,0.0),(0.0,0.0,0.866)],
    "locator": [(0.0,0.0,1.0),(0.0,0.0,-1.0),(0.0,0.0,0.0),(-1.0,0.0,0.0),(1.0,0.0,0.0),(0.0,0.0,0.0),(0.0,1.0,0.0),(0.0,-1.0,0.0)],
    "eye": [(-1.777,0.0,0.0),(-1.401,-0.706,0.0),(-0.473,-0.321,0.0),(0.473,-0.321,0.0),(1.403,-0.706,0.0),(1.812,0.0,0.0),(1.403,0.706,0.0),(0.473,0.321,0.0),(-0.473,0.321,0.0),(-1.401,0.706,0.0),(-1.777,0.0,0.0)],
}
_SHAPE_ALIASES = {"cube": "box"}


def _cmds():
    import maya.cmds as cmds
    return cmds


def available_shapes(): return tuple(sorted(set(_SHAPES) | set(_SHAPE_ALIASES)))
def _canonical_shape(shape): return _SHAPE_ALIASES.get(shape, shape)

def _scaled_points(shape, size):
    shape = _canonical_shape(shape)
    if shape not in _SHAPES: raise ValueError("Unsupported control shape: {0}".format(shape))
    size = float(size)
    if size <= 0.0: raise ValueError("Control size must be greater than zero.")
    return [(x*size,y*size,z*size) for x,y,z in _SHAPES[shape]]

def normalize_curve_shape_data(data):
    """Normalize one serialized AS curve shape without importing Maya."""
    if not isinstance(data, dict): raise TypeError("Curve shape data must be a dictionary")
    degree = int(data.get("degree", 1)); form = int(data.get("form", 0))
    if degree < 1: raise ValueError("Curve degree must be at least 1.")
    raw = data.get("points", data.get("pointData", []))
    if isinstance(raw, dict):
        def key(item):
            name = str(item[0]); digits = "".join(c for c in name if c.isdigit()); return int(digits) if digits else name
        raw = [value for _, value in sorted(raw.items(), key=key)]
    points = tuple(tuple(float(v) for v in point) for point in (raw or []))
    if any(len(point) != 3 for point in points): raise ValueError("Curve points must contain XYZ triples.")
    if len(points) < degree + 1: raise ValueError("Curve data does not contain enough points for its degree.")
    result = {"degree": degree, "form": form, "points": points}
    if "knots" in data and data["knots"] is not None: result["knots"] = tuple(float(v) for v in data["knots"])
    return result

def _remap_shape_plug(plug, old_shape, new_shape):
    prefix = old_shape + "."
    return new_shape + plug[len(old_shape):] if plug.startswith(prefix) else plug

def _curve_shape(cmds, node):
    if not node or not cmds.objExists(node): raise ValueError("Control does not exist: {0}".format(node))
    if cmds.nodeType(node) == "nurbsCurve":
        parents = cmds.listRelatives(node,parent=True,fullPath=True) or []
        if not parents: raise ValueError("Curve shape has no transform parent: {0}".format(node))
        return parents[0], cmds.ls(node,long=True)[0]
    shapes = cmds.listRelatives(node,shapes=True,type="nurbsCurve",fullPath=True) or []
    if not shapes: raise ValueError("Control has no nurbsCurve shape: {0}".format(node))
    return cmds.ls(node,long=True)[0], shapes[0]

def create_control(name, shape="circle", size=1.0, match=None, parent=None):
    cmds=_cmds(); control=cmds.curve(name=name,degree=1,point=_scaled_points(shape,size))
    if match:
        if not cmds.objExists(match): cmds.delete(control); raise ValueError("Match target does not exist: {0}".format(match))
        cmds.xform(control,worldSpace=True,matrix=cmds.xform(match,query=True,worldSpace=True,matrix=True))
    if parent:
        if not cmds.objExists(parent): cmds.delete(control); raise ValueError("Parent does not exist: {0}".format(parent))
        cmds.parent(control,parent)
    return control

def replace_control_shape(node, shape="circle", size=1.0):
    cmds=_cmds(); points=_scaled_points(shape,size); transform,old_shape=_curve_shape(cmds,node); old_short=old_shape.split("|")[-1]
    incoming=cmds.listConnections(old_shape,source=True,destination=False,plugs=True,connections=True) or []; outgoing=cmds.listConnections(old_shape,source=False,destination=True,plugs=True,connections=True) or []; cmds.delete(old_shape)
    temp=cmds.curve(name=transform.split("|")[-1]+"_shapeTmp",degree=1,point=points); temp_shape=(cmds.listRelatives(temp,shapes=True,type="nurbsCurve",fullPath=True) or [None])[0]
    if not temp_shape: cmds.delete(temp); raise RuntimeError("Temporary control curve did not produce a nurbsCurve shape.")
    parented=cmds.parent(temp_shape,transform,shape=True,relative=True)[0]; cmds.delete(temp); new_shape=cmds.ls(cmds.rename(parented,old_short),long=True)[0]
    for index in range(0,len(incoming),2): cmds.connectAttr(incoming[index+1],_remap_shape_plug(incoming[index],old_shape,new_shape),force=True)
    for index in range(0,len(outgoing),2): cmds.connectAttr(_remap_shape_plug(outgoing[index],old_shape,new_shape),outgoing[index+1],force=True)
    return transform,new_shape

def create_zero_group(node, suffix="_ZERO"):
    cmds=_cmds()
    if not cmds.objExists(node): raise ValueError("Node does not exist: {0}".format(node))
    parent=cmds.listRelatives(node,parent=True,fullPath=True) or []; matrix=cmds.xform(node,query=True,worldSpace=True,matrix=True); group=cmds.createNode("transform",name="{0}{1}".format(node.split("|")[-1],suffix)); cmds.xform(group,worldSpace=True,matrix=matrix)
    if parent: group=cmds.parent(group,parent[0])[0]; cmds.xform(group,worldSpace=True,matrix=matrix)
    return group,cmds.parent(node,group)[0]

def create_controls_for_nodes(nodes, shape="circle", size=1.0, suffix="_CTRL"):
    return [create_control(node.split("|")[-1]+suffix,shape=shape,size=size,match=node) for node in nodes]
