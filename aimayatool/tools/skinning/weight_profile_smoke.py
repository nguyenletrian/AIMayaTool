from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from . import weight_profile


def run_weight_profile_smoke():
    # Managed live validation can reuse a Maya process across repository updates.
    # Reload the product module so the smoke always executes the current file on disk.
    importlib.reload(weight_profile)
    cmds.file(new=True, force=True)
    name = weight_profile.DEFAULT_PROFILE
    created = weight_profile.ensure_profile(name)
    if created != name or not cmds.objExists(name):
        raise RuntimeError("weight profile creation failed")
    start = weight_profile.sample_profile(0.0, name)
    end = weight_profile.sample_profile(1.0, name)
    mid = weight_profile.sample_profile(0.5, name)
    if abs(start) > 1e-6 or abs(end - 1.0) > 1e-6:
        raise RuntimeError("weight profile endpoints are invalid: %s %s" % (start, end))
    if mid < -1e-6 or mid > 1.0 + 1e-6:
        raise RuntimeError("weight profile midpoint is outside normalized range: %s" % mid)
    weight_profile.reset_profile(name)
    return "SKINNING_WEIGHT_PROFILE_SMOKE_OK"
