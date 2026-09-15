from __future__ import absolute_import

from aimayatool.tools.setup.controls import available_shapes, replace_control_shape


def _cmds():
    import maya.cmds as cmds
    return cmds


def apply_control_shape_preset(objects, shape="circle", size=1.0):
    """Apply one supported AIMayaTool control-shape preset to explicit controls."""
    cmds = _cmds()
    shape = str(shape).strip().lower()
    if shape not in available_shapes():
        raise ValueError("Unsupported control shape: {0}".format(shape))
    results = []
    for obj in tuple(objects or ()):
        if not obj or not cmds.objExists(obj):
            results.append({"object": obj, "status": "skipped_missing"})
            continue
        try:
            transform, curve_shape = replace_control_shape(obj, shape=shape, size=size)
        except ValueError as exc:
            results.append({"object": obj, "status": "skipped_invalid_control", "error": str(exc)})
            continue
        results.append({"object": obj, "status": "applied", "transform": transform, "shape": curve_shape, "preset": shape})
    return tuple(results)
