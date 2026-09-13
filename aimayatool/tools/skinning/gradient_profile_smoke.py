from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import gradient_profile
from . import weight_profile


def run_gradient_profile_smoke():
    cmds.file(new=True, force=True)
    importlib.invalidate_caches()
    importlib.reload(weight_profile)
    importlib.reload(gradient_profile)
    name = 'AIMayaToolGradientProfileSmoke'
    weight_profile.reset_profile(name)
    values = gradient_profile.sample_distance_profile([0.0, 5.0, 10.0], sampler=lambda ratio: weight_profile.sample_profile(ratio, name=name, create=False))
    if len(values) != 3:
        raise RuntimeError('gradient profile returned unexpected sample count: %s' % values)
    if abs(values[0] - 1.0) > 1e-6 or abs(values[-1]) > 1e-6:
        raise RuntimeError('gradient profile endpoints are invalid: %s' % values)
    if any(value < -1e-6 or value > 1.0 + 1e-6 for value in values):
        raise RuntimeError('gradient profile returned value outside normalized range: %s' % values)
    return 'SKINNING_GRADIENT_PROFILE_SMOKE_OK'
