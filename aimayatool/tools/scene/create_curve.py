"""Deterministic ScenePattern CreateCurve composition with a thin Maya execution boundary."""


def _cmds():
    import maya.cmds as cmds
    return cmds


def normalize_points(points):
    if isinstance(points, str):
        points = [line.strip().split() for line in points.splitlines() if line.strip()]
    result = tuple(tuple(float(value) for value in point) for point in (points or ()))
    if any(len(point) != 3 for point in result):
        raise ValueError("Each curve point must contain exactly three values.")
    return result


def build_create_curve_plan(item):
    if not isinstance(item, dict):
        raise TypeError("CreateCurve item must be a dictionary.")
    points = normalize_points(item.get("points", ()))
    if len(points) < 2:
        raise ValueError("Need at least two points to create a curve.")
    name = item.get("curve_name") or item.get("curveName")
    if not name:
        raise ValueError("curve_name is required.")
    return {"points": points, "curve_name": str(name), "parent": item.get("parent") or None, "degree": min(3, len(points)-1), "hidden": bool(item.get("hidden", True)), "rebuild_spans": int(item.get("rebuild_spans", item.get("rebuild", 0)) or 0)}


def build_create_curve_plans(items):
    return tuple(build_create_curve_plan(item) for item in (items or ()))


def execute_create_curve_plan(plan, cmds_module=None):
    cmds = cmds_module or _cmds(); parent = plan["parent"]
    if parent and not cmds.objExists(parent): parent = None
    curve = cmds.curve(point=plan["points"], degree=plan["degree"], name=plan["curve_name"])
    if plan["hidden"]: cmds.setAttr(curve+".visibility", 0)
    if parent: curve = cmds.parent(curve, parent)[0]
    rebuilt = None
    if plan["rebuild_spans"] > 0:
        result = cmds.rebuildCurve(curve, constructionHistory=True, replaceOriginal=False, rebuildType=0, endKnots=True, keepRange=False, keepControlPoints=False, keepEndPoints=True, keepTangents=False, spans=plan["rebuild_spans"], degree=3, tolerance=0.01)
        rebuilt = cmds.rename(result[0], plan["curve_name"]+"_Rebuild")
        if plan["hidden"]: cmds.setAttr(rebuilt+".visibility", 0)
        if parent: rebuilt = cmds.parent(rebuilt, parent)[0]
    return {"curve":curve,"rebuilt_curve":rebuilt,"degree":plan["degree"],"point_count":len(plan["points"]),"rebuild_spans":plan["rebuild_spans"]}


def create_curve(points, curve_name, parent=None, rebuild_spans=0, hidden=True):
    return execute_create_curve_plan(build_create_curve_plan({"points":points,"curve_name":curve_name,"parent":parent,"rebuild_spans":rebuild_spans,"hidden":hidden}))


def create_curves(items):
    results=[]
    for item in items or ():
        try: results.append(execute_create_curve_plan(build_create_curve_plan(item)))
        except ValueError as exc: results.append({"status":"skipped","reason":str(exc),"item":item})
    return tuple(results)
