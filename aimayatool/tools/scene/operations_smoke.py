from __future__ import absolute_import, print_function

import os
import shutil
import tempfile

from aimayatool.tools.scene.operations import create_pattern, edit_pattern, load_pattern, save_pattern


def run():
    source = create_pattern("demo", label="Source", nodes=["a"], metadata={"value": 1})
    edited = edit_pattern(source, label="Edited", nodes=["a", "b"])
    assert source.label == "Source"
    assert source.nodes == ["a"]
    assert edited.label == "Edited"
    assert edited.nodes == ["a", "b"]
    assert edited.pattern_id == source.pattern_id

    root = tempfile.mkdtemp(prefix="aimayatool_scene_pattern_")
    try:
        path = os.path.join(root, "pattern.json")
        saved = save_pattern(edited, path)
        assert saved == os.path.abspath(path)
        restored = load_pattern(path)
        assert restored.to_dict() == edited.to_dict()
        try:
            save_pattern(edited, path)
        except IOError:
            pass
        else:
            raise AssertionError("save_pattern must reject overwrite by default")
        save_pattern(source, path, overwrite=True)
        assert load_pattern(path).to_dict() == source.to_dict()
    finally:
        shutil.rmtree(root)
    print("AIMAYATOOL_SCENE_OPERATIONS_SMOKE_OK")


if __name__ == "__main__":
    run()
