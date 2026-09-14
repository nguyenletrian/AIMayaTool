from __future__ import absolute_import

from .global_plan import build_global_pattern_plan


plan = build_global_pattern_plan({
    "parent": "Global_CTRL",
    "child": "arm_L_CTRL\narm_R_CTRL",
    "attrSlide": "Global",
    "defaultValue": "0.25",
    "maintain": True,
})
if len(plan) != 2:
    raise AssertionError("Expected one operation per child.")
if [item["child"] for item in plan] != ["arm_L_CTRL", "arm_R_CTRL"]:
    raise AssertionError("Global plan child order is not deterministic.")
if plan[0]["parent"] != "Global_CTRL" or plan[0]["attr_name"] != "Global":
    raise AssertionError("Global plan lost normalized identity fields.")
if plan[0]["default_value"] != 0.25 or plan[0]["maintain_offset"] is not True:
    raise AssertionError("Global plan lost normalized option values.")

empty = build_global_pattern_plan({
    "parent": "Global_CTRL",
    "child": [],
    "attrSlide": "Global",
    "defaultValue": 0,
    "maintain": False,
})
if empty != ():
    raise AssertionError("Empty children must produce an empty plan.")

SMOKE_MARKER = "SCENE_GLOBAL_PATTERN_PLAN_OK:5"
