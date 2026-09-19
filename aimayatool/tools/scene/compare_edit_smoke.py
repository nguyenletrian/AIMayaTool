from __future__ import absolute_import

from .compare_edit import apply_pattern_changes, compare_patterns
from .patterns import ScenePattern


def run():
    source = ScenePattern("walk", label="Walk", nodes=["root"], metadata={"group": "body"})
    same = ScenePattern.from_dict(source.to_dict())
    assert compare_patterns(source, same) == {"changed": False, "changes": []}
    edited = apply_pattern_changes(source, {"label": "Walk v2", "nodes": ["root", "foot"]})
    assert source.label == "Walk" and source.nodes == ["root"]
    diff = compare_patterns(source, edited)
    assert diff["changed"] is True
    assert [item["field"] for item in diff["changes"]] == ["label", "nodes"]
    assert diff["changes"][0]["before"] == "Walk" and diff["changes"][0]["after"] == "Walk v2"
    try:
        apply_pattern_changes(source, {"unknown": 1})
        raise AssertionError("unknown field unexpectedly accepted")
    except ValueError:
        pass
    try:
        compare_patterns(source, object())
        raise AssertionError("invalid comparison unexpectedly accepted")
    except TypeError:
        pass
    return "SCENE_COMPARE_EDIT_BEHAVIOR_OK"


RESULT = run()
assert RESULT == "SCENE_COMPARE_EDIT_BEHAVIOR_OK"
