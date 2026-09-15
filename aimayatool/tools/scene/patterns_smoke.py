from __future__ import absolute_import, print_function

from aimayatool.tools.scene.patterns import PatternRegistry, ScenePattern


def run():
    pattern = ScenePattern("demo", label="Demo", nodes=["a", "b"], metadata={"kind": "test"})
    payload = pattern.to_json()
    restored = ScenePattern.from_json(payload)
    assert restored.to_dict() == pattern.to_dict()
    assert ScenePattern.from_json(pattern.to_json()).to_json() == pattern.to_json()

    try:
        ScenePattern.from_dict({"version": 999, "pattern_id": "bad"})
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported ScenePattern version must fail")

    registry = PatternRegistry()
    registry.register(pattern)
    assert registry.get("demo") is pattern
    assert registry.ids() == ["demo"]
    try:
        registry.register(pattern)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate pattern registration must fail")
    replacement = ScenePattern("demo", label="Replacement")
    registry.register(replacement, replace=True)
    assert registry.get("demo") is replacement
    assert registry.remove("demo") is replacement
    assert registry.ids() == []
    print("AIMAYATOOL_SCENE_PATTERN_SMOKE_OK")


if __name__ == "__main__":
    run()
