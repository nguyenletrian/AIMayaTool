from __future__ import absolute_import


DEFAULT_PROFILE = "AIMayaToolWeightProfile"


def _cmds():
    import maya.cmds as cmds
    return cmds


def ensure_profile(name=DEFAULT_PROFILE):
    """Ensure a normalized 0..1 skin-weight profile backed by an animCurveTU."""
    cmds = _cmds()
    if cmds.objExists(name):
        return name
    curve = cmds.createNode("animCurveTU", name=name)
    cmds.setKeyframe(curve, time=0.0, value=0.0)
    cmds.setKeyframe(curve, time=100.0, value=100.0)
    cmds.keyTangent(curve, itt="flat", ott="flat")
    return curve


def sample_profile(ratio, name=DEFAULT_PROFILE, create=True):
    """Sample a normalized profile ratio in [0, 1] and return a normalized value."""
    ratio = float(ratio)
    if ratio < 0.0 or ratio > 1.0:
        raise ValueError("ratio must be between 0.0 and 1.0")
    cmds = _cmds()
    if not cmds.objExists(name):
        if not create:
            raise ValueError("Weight profile does not exist: {0}".format(name))
        ensure_profile(name)
    return float(cmds.getAttr(name + ".output", time=ratio * 100.0)) / 100.0


def reset_profile(name=DEFAULT_PROFILE, outgoing="flat", incoming="flat"):
    """Reset a profile to two endpoint keys while keeping the node reusable."""
    cmds = _cmds()
    ensure_profile(name)
    keys = cmds.keyframe(name, query=True, timeChange=True) or []
    for key in keys:
        if abs(key) > 1e-8 and abs(key - 100.0) > 1e-8:
            cmds.cutKey(name, time=(key, key), clear=True)
    cmds.setKeyframe(name, time=0.0, value=0.0)
    cmds.setKeyframe(name, time=100.0, value=100.0)
    cmds.keyTangent(name, time=(0.0, 0.0), ott=outgoing)
    cmds.keyTangent(name, time=(100.0, 100.0), itt=incoming)
    return name
