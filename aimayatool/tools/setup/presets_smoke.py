from __future__ import absolute_import

from . import presets


def _expect_value_error(callable_obj, contains):
    try:
        callable_obj()
    except ValueError as exc:
        if contains not in str(exc):
            raise AssertionError("Expected error containing {0!r}, got {1!r}".format(contains, str(exc)))
        return
    raise AssertionError("Expected ValueError containing {0!r}".format(contains))


def run_setup_presets_smoke():
    builtins = presets.builtin_control_presets()
    if sorted(builtins) != ["fk", "ik", "pole"]:
        raise AssertionError("Unexpected built-in preset keys: {0}".format(sorted(builtins)))
    if builtins["fk"]["shape"] != "circle" or builtins["ik"]["shape"] != "box" or builtins["pole"]["shape"] != "locator":
        raise AssertionError("Built-in preset shapes are not canonical: {0}".format(builtins))

    request = presets.preflight_control_batch_request(["root_JNT", "spine_JNT"], {"name": "custom", "shape": "cube", "size": 2, "suffix": "_CTL"})
    if request["count"] != 2 or request["preset"]["shape"] != "cube" or request["preset"]["size"] != 2.0:
        raise AssertionError("Unexpected normalized request: {0}".format(request))

    _expect_value_error(lambda: presets.preflight_control_batch_request([], builtins["fk"]), "At least one source node")
    _expect_value_error(lambda: presets.preflight_control_batch_request(["arm_JNT", "arm_JNT"], builtins["fk"]), "Duplicate source node")
    _expect_value_error(lambda: presets.normalize_control_preset({"name": "bad", "shape": "triangle"}), "Unsupported control shape")
    _expect_value_error(lambda: presets.normalize_control_preset({"name": "bad", "size": 0}), "greater than zero")
    _expect_value_error(lambda: presets.normalize_control_preset({"name": "bad", "unknown": True}), "Unsupported control preset fields")
    return "SETUP_PRESETS_PREFLIGHT_OK:8"


_RESULT = run_setup_presets_smoke()
