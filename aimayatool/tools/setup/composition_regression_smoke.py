from __future__ import absolute_import

import importlib


def _module(name):
    return importlib.import_module("aimayatool.tools.setup." + name)


def _run(module_name, callable_name, expected):
    module = importlib.reload(_module(module_name))
    result = getattr(module, callable_name)()
    if result != expected:
        raise RuntimeError("Unexpected Setup composition result: {0} != {1}".format(result, expected))
    return result


def run_setup_composition_baseline_regression():
    checks = (
        ("constraint_smoke", "run_setup_constraint_primitives_smoke", "SETUP_CONSTRAINT_PRIMITIVES_SMOKE_OK:4"),
        ("space_smoke", "run_setup_space_switch_smoke", "SETUP_SPACE_SWITCH_SMOKE_OK:2"),
        ("ikfk_smoke", "run_setup_ikfk_blend_smoke", "SETUP_IKFK_BLEND_SMOKE_OK:2"),
        ("ikfk_smoke", "run_setup_rp_ik_smoke", "SETUP_RP_IK_SMOKE_OK:1"),
        ("ikfk_smoke", "run_setup_ikfk_switch_smoke", "SETUP_IKFK_SWITCH_SMOKE_OK:2"),
        ("ikfk_smoke", "run_setup_ikfk_snap_smoke", "SETUP_IKFK_SNAP_SMOKE_OK:2"),
        ("sdk_smoke", "run_setup_sdk_smoke", "SETUP_SDK_SMOKE_OK:1"),
        ("sdk_smoke", "run_setup_sdk_proxy_attr_smoke", "SETUP_SDK_PROXY_ATTR_SMOKE_OK:1"),
        ("sdk_smoke", "run_setup_modulo_sdk_smoke", "SETUP_MODULO_SDK_SMOKE_OK:3"),
        ("spline_composition_smoke", "run_setup_spline_composition_smoke", "SETUP_SPLINE_COMPOSITION_SMOKE_OK:4"),
    )
    for module_name, callable_name, expected in checks:
        _run(module_name, callable_name, expected)
    return "SETUP_COMPOSITION_BASELINE_OK:{0}".format(len(checks))
