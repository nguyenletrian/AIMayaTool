from __future__ import absolute_import

from .control_shape import apply_control_shapes, build_control_shape_plan


def run_scene_control_shape_python_smoke():
    plan = build_control_shape_plan([
        {"objects": "Arm_L_CTRL\nArm_R_CTRL", "shape": "cube", "size": "2.5"},
        {"objects": ["Head_CTRL"], "controlShape": "circle", "size": 1},
    ])
    if plan != [
        {"object": "Arm_L_CTRL", "shape": "cube", "size": 2.5},
        {"object": "Arm_R_CTRL", "shape": "cube", "size": 2.5},
        {"object": "Head_CTRL", "shape": "circle", "size": 1.0},
    ]:
        raise RuntimeError("ControlShape plan mismatch: {0}".format(plan))
    calls = []
    def fake_replace(node, shape="circle", size=1.0):
        calls.append((node, shape, size)); return node, node + "Shape"
    result = apply_control_shapes([{"objects": ["Main_CTRL", "COG_CTRL"], "shape": "box", "size": 3}], fake_replace)
    if calls != [("Main_CTRL", "box", 3.0), ("COG_CTRL", "box", 3.0)]:
        raise RuntimeError("Setup delegation mismatch: {0}".format(calls))
    if [item["shape_node"] for item in result] != ["Main_CTRLShape", "COG_CTRLShape"]:
        raise RuntimeError("ControlShape result mismatch")
    return "SCENE_CONTROL_SHAPE_PYTHON_SMOKE_OK:3"


RESULT = run_scene_control_shape_python_smoke()
print(RESULT)
