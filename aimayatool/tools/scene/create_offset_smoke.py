"""Python-only deterministic smoke for ScenePattern Create Offset composition."""

from __future__ import absolute_import

from .create_offset import build_create_offset_plan, create_offsets, normalize_create_offset_item


def run_scene_create_offset_smoke():
    normalized = normalize_create_offset_item({"objects": "A_CTRL\n\n B_CTRL ", "extraName": "_SceneOffset"})
    assert normalized == {"objects": ("A_CTRL", "B_CTRL"), "suffix": "_SceneOffset"}
    assert normalize_create_offset_item({"objects": ["C_CTRL"], "extraName": ""})["suffix"] == "_ZERO"

    plan = build_create_offset_plan([
        {"objects": "A_CTRL\nB_CTRL", "extraName": "_SceneOffset"},
        {"objects": ["Missing_CTRL"], "suffix": "_Custom"},
    ])
    assert plan == (
        {"object": "A_CTRL", "suffix": "_SceneOffset"},
        {"object": "B_CTRL", "suffix": "_SceneOffset"},
        {"object": "Missing_CTRL", "suffix": "_Custom"},
    )

    calls = []
    def fake_zero(node, suffix="_ZERO"):
        calls.append((node, suffix))
        return node + suffix, node
    results = create_offsets([
        {"objects": ["A_CTRL", "Missing_CTRL"], "extraName": "_SceneOffset"}
    ], create_zero_group_fn=fake_zero, exists_fn=lambda node: node != "Missing_CTRL")
    assert calls == [("A_CTRL", "_SceneOffset")]
    assert results[0]["status"] == "applied" and results[0]["group"] == "A_CTRL_SceneOffset"
    assert results[1] == {"object": "Missing_CTRL", "status": "skipped_missing"}

    marker = "SCENE_CREATE_OFFSET_PYTHON_SMOKE_OK:2"
    print(marker)
    return marker


SMOKE_RESULT = run_scene_create_offset_smoke()
