from __future__ import absolute_import

from .patterns import PatternRegistry, ScenePattern


def run_scene_pattern_smoke():
    pattern = ScenePattern(
        "basic-rig",
        label="Basic Rig",
        nodes=[{"name": "root", "type": "transform"}],
        metadata={"category": "setup"},
    )
    restored = ScenePattern.from_json(pattern.to_json())
    assert restored.to_dict() == pattern.to_dict()

    registry = PatternRegistry()
    registry.register(restored)
    assert registry.ids() == ["basic-rig"]
    assert registry.get("basic-rig").label == "Basic Rig"

    duplicate_rejected = False
    try:
        registry.register(restored)
    except ValueError:
        duplicate_rejected = True
    assert duplicate_rejected

    registry.register(ScenePattern("basic-rig", label="Replacement"), replace=True)
    assert registry.get("basic-rig").label == "Replacement"
    assert registry.remove("basic-rig") is not None
    assert registry.ids() == []
    return "SCENE_PATTERN_SMOKE_OK"
