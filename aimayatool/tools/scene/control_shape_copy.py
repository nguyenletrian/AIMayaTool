from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _curve_shapes(cmds, node):
    return tuple(cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True, type="nurbsCurve") or ())


def copy_curve_shape(source, targets):
    """Replace target curve shapes with source shapes while preserving target transforms."""
    cmds = _cmds()
    if not source or not cmds.objExists(source):
        raise ValueError("Source does not exist: {0}".format(source))
    source_shapes = _curve_shapes(cmds, source)
    if not source_shapes:
        raise ValueError("Source has no NURBS curve shapes: {0}".format(source))
    results = []
    for target in tuple(targets or ()):
        if not target or not cmds.objExists(target):
            results.append({"target": target, "status": "skipped_missing"}); continue
        old_shapes = _curve_shapes(cmds, target)
        visibility_source = cmds.connectionInfo(old_shapes[0] + ".visibility", sourceFromDestination=True) if old_shapes else ""
        duplicate = cmds.duplicate(source, returnRootsOnly=True)[0]
        dup_shapes = _curve_shapes(cmds, duplicate)
        for shape in dup_shapes:
            cmds.parent(shape, target, relative=True, shape=True)
        cmds.delete(duplicate)
        for shape in old_shapes:
            cmds.lockNode(shape, lock=False); cmds.delete(shape)
        new_shapes = _curve_shapes(cmds, target)
        for index, shape in enumerate(new_shapes):
            desired = old_shapes[index].split("|")[-1] if index < len(old_shapes) else target.split("|")[-1] + "Shape{0}".format(index + 1)
            shape = cmds.rename(shape, desired)
            if visibility_source:
                cmds.connectAttr(visibility_source, shape + ".visibility", force=True)
        results.append({"target": target, "status": "copied", "shape_count": len(new_shapes)})
    return tuple(results)


def mirror_curve_shape(source, target, axis="x"):
    """Mirror source CV world positions onto an existing target curve shape topology."""
    cmds = _cmds(); axis = str(axis).lower()
    if axis not in ("x", "y", "z"):
        raise ValueError("axis must be x, y or z")
    if not source or not cmds.objExists(source) or not target or not cmds.objExists(target):
        return {"status": "skipped_missing", "source": source, "target": target}
    source_shapes, target_shapes = _curve_shapes(cmds, source), _curve_shapes(cmds, target)
    if len(source_shapes) != len(target_shapes):
        return {"status": "skipped_shape_mismatch", "source": source, "target": target}
    axis_index = {"x": 0, "y": 1, "z": 2}[axis]
    count = 0
    for src_shape, dst_shape in zip(source_shapes, target_shapes):
        src_cvs = cmds.ls(src_shape + ".cv[*]", flatten=True) or []
        dst_cvs = cmds.ls(dst_shape + ".cv[*]", flatten=True) or []
        if len(src_cvs) != len(dst_cvs):
            return {"status": "skipped_cv_mismatch", "source": source, "target": target}
        for src_cv, dst_cv in zip(src_cvs, dst_cvs):
            point = list(cmds.pointPosition(src_cv, world=True)); point[axis_index] *= -1.0
            cmds.xform(dst_cv, worldSpace=True, translation=point); count += 1
    return {"status": "mirrored", "source": source, "target": target, "cv_count": count}
