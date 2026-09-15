from __future__ import absolute_import

from .create_attribute import build_attribute_spec, build_create_attribute_plan, create_attribute


def run_scene_create_attribute_python_smoke():
    spec = build_attribute_spec("mode", "enum", False, True, True, 0, 2, 1, "FK:IK:Auto")
    if spec["name"] != "mode" or spec["enum"] != "FK:IK:Auto":
        raise RuntimeError("Scene attribute normalization mismatch")
    plan = build_create_attribute_plan(["A", "B"], "mode", "enum", False, True, True, 0, 2, 1, "FK:IK:Auto")
    if tuple(item["object"] for item in plan) != ("A", "B"):
        raise RuntimeError("Scene attribute plan mismatch")
    calls = []
    def fake_create(node, attribute, **kwargs):
        calls.append((node, attribute, dict(kwargs)))
        return node + "." + attribute
    result = create_attribute(["A", "B"], "mode", "enum", False, True, True, 0, 2, 1,
                              "FK:IK:Auto", create_attribute_fn=fake_create)
    if tuple(item["status"] for item in result) != ("created", "created"):
        raise RuntimeError("Scene composition status mismatch")
    if [call[0] for call in calls] != ["A", "B"] or calls[0][2]["enum"] != "FK:IK:Auto":
        raise RuntimeError("Scene did not delegate normalized data to Setup boundary")
    return "SCENE_CREATE_ATTRIBUTE_PYTHON_SMOKE_OK:2"


RESULT = run_scene_create_attribute_python_smoke()
print(RESULT)
