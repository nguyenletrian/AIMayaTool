from __future__ import absolute_import

from .pattern_descriptor import normalize_scene_pattern_descriptor


def run_scene_pattern_descriptor_smoke():
    value = normalize_scene_pattern_descriptor({
        "parent": "Global_CTRL",
        "child": "Arm_L_CTRL\nArm_R_CTRL\n",
        "attrSlide": "Global",
        "defaultValue": "0.25",
        "maintain": True,
    })
    if value["children"] != ("Arm_L_CTRL", "Arm_R_CTRL"):
        raise AssertionError("Child normalization failed.")
    if value["default_value"] != 0.25 or value["attr_slide"] != "Global":
        raise AssertionError("Descriptor scalar normalization failed.")

    failed = 0
    for bad in (
        {"child": 123},
        {"defaultValue": "abc"},
        {"maintain": 1},
        {"unknown": True},
    ):
        try:
            normalize_scene_pattern_descriptor(bad)
        except (TypeError, ValueError):
            failed += 1
    if failed != 4:
        raise AssertionError("Descriptor invalid-input guards failed: {0}".format(failed))
    return "SCENE_PATTERN_DESCRIPTOR_SMOKE_OK:6"


_SMOKE_RESULT = run_scene_pattern_descriptor_smoke()
