from __future__ import absolute_import

import importlib

from . import smoke as smoke_module


def run_setup_controls_transforms_regression():
    smoke = importlib.reload(smoke_module)
    checks = (
        (smoke.run_setup_controls_smoke, "SETUP_CONTROLS_SMOKE_OK"),
        (smoke.run_setup_control_shape_catalog_smoke, "SETUP_CONTROL_SHAPE_CATALOG_SMOKE_OK:5"),
        (smoke.run_setup_transform_primitives_smoke, "SETUP_TRANSFORM_PRIMITIVES_SMOKE_OK:3"),
        (smoke.run_setup_match_joint_chain_smoke, "SETUP_MATCH_JOINT_CHAIN_SMOKE_OK:4"),
        (smoke.run_setup_control_shape_replace_smoke, "SETUP_CONTROL_SHAPE_REPLACE_SMOKE_OK:1"),
    )
    for runner, expected in checks:
        result = runner()
        if result != expected:
            raise RuntimeError("Unexpected Setup regression result: {0} != {1}".format(result, expected))
    return "SETUP_CONTROLS_TRANSFORMS_REGRESSION_OK:5"
