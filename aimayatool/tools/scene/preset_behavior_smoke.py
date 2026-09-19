from __future__ import absolute_import

import shutil
import tempfile

from .patterns import ScenePattern
from .presets import PresetLibrary


def run():
    root = tempfile.mkdtemp(prefix="aimayatool_scene_presets_")
    try:
        library = PresetLibrary(root)
        library.save("zeta", ScenePattern("z", nodes=["nodeA"]))
        library.save("alpha", ScenePattern("a"))
        assert library.list() == ["alpha", "zeta"]
        assert library.get("zeta").pattern_id == "z"
        try:
            library.save("zeta", ScenePattern("replacement"))
            raise AssertionError("duplicate save unexpectedly succeeded")
        except IOError:
            pass
        library.save("zeta", ScenePattern("replacement"), overwrite=True)
        assert library.get("zeta").pattern_id == "replacement"
        for name in ("", ".", "..", "../escape", "a/b", "a\\\\b"):
            try:
                library.path(name)
                raise AssertionError("invalid preset name accepted: {0}".format(name))
            except ValueError:
                pass
        assert library.delete("alpha") is True
        assert library.get("alpha") is None
        assert library.delete("alpha", missing_ok=True) is False
        try:
            library.delete("alpha")
            raise AssertionError("missing delete unexpectedly succeeded")
        except IOError:
            pass
        return "SCENE_PRESET_BEHAVIOR_OK"
    finally:
        shutil.rmtree(root, ignore_errors=True)


RESULT = run()
assert RESULT == "SCENE_PRESET_BEHAVIOR_OK"
