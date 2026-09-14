"""ScenePattern curve creation migrated from MayaScriptNew."""


def _cmds():
    import maya.cmds as cmds
    return cmds


def normalize_points(points):
    """Return explicit XYZ tuples from a string or iterable of point triples."""
    if isinstance(points, str):
        rows = []
        for line in points.splitlines():
            line = line.strip()
            if line:
                rows.append(tuple(float(value) for value in line.split()))
        points = rows
    result = []
    for point in points or ():
        if len(point) != 3:
            raise ValueError("Each curve point must contain exactly three values.")
        result.append(tuple(float(value) for value in point))
    return tuple(result)


def create_curve(points, curve_name, parent=None, rebuild_spans=0, hidden=True):
    """Create one deterministic curve and optionally rebuild it with explicit spans."""
    cmds = _cmds()
    points = normalize_points(points)
    if len(points) < 2:
        raise ValueError("Need at least two points to create a curve.")
    if not curve_name:
        raise ValueError("curve_name is required.")
    if parent and not cmds.objExists(parent):
        parent = None

    degree = min(3, len(points) - 1)
    curve = cmds.curve(point=points, degree=degree, name=curve_name)
    if hidden:
        cmds.setAttr(curve + ".visibility", 0)
    if parent:
        curve = cmds.parent(curve, parent)[0]

    rebuilt = None
    spans = int(rebuild_spans or 0)
    if spans > 0:
        result = cmds.rebuildCurve(
            curve, constructionHistory=True, replaceOriginal=False,
            rebuildType=0, endKnots=True, keepRange=False,
            keepControlPoints=False, keepEndPoints=True, keepTangents=False,
            spans=spans, degree=3, tolerance=0.01,
        )
        rebuilt = cmds.rename(result[0], curve_name + "_Rebuild")
        if hidden:
            cmds.setAttr(rebuilt + ".visibility", 0)
        if parent:
            rebuilt = cmds.parent(rebuilt, parent)[0]

    return {
        "curve": curve,
        "rebuilt_curve": rebuilt,
        "degree": degree,
        "point_count": len(points),
        "rebuild_spans": spans,
    }


def create_curves(items):
    """Create multiple curves from explicit item dictionaries."""
    results = []
    for item in items or ():
        try:
            results.append(create_curve(
                points=item.get("points", ()),
                curve_name=item.get("curve_name") or item.get("curveName"),
                parent=item.get("parent"),
                rebuild_spans=item.get("rebuild_spans", item.get("rebuild", 0)),
                hidden=item.get("hidden", True),
            ))
        except ValueError as exc:
            results.append({"status": "skipped", "reason": str(exc), "item": item})
    return tuple(results)
