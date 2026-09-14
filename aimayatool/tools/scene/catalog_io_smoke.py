from __future__ import absolute_import

import os
import tempfile

from .catalog import ScenePatternCatalog, ScenePatternEntry
from .catalog_io import load_catalog, save_catalog


def run_scene_pattern_catalog_io_smoke():
    catalog = ScenePatternCatalog([
        ScenePatternEntry("a", "Scene_Pattern_Global", "global.json", order=0, title="Global", name="Global"),
        ScenePatternEntry("b", "Scene_Pattern_Layer", "layer.json", order=1, title="Layer", name="Layer"),
    ])
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "ScenePatternData.json")
        saved = save_catalog(catalog, path)
        if saved != os.path.abspath(path) or not os.path.isfile(saved):
            raise AssertionError("Catalog save did not produce the expected file.")
        loaded = load_catalog(saved)
        if loaded.to_dict() != catalog.to_dict():
            raise AssertionError("Catalog file round trip failed.")
        overwrite_rejected = False
        try:
            save_catalog(catalog, saved)
        except IOError:
            overwrite_rejected = True
        if not overwrite_rejected:
            raise AssertionError("Catalog overwrite was not guarded.")
        save_catalog(catalog, saved, overwrite=True)
        if load_catalog(saved).to_dict() != catalog.to_dict():
            raise AssertionError("Explicit catalog overwrite did not preserve data.")
    return "SCENE_PATTERN_CATALOG_IO_SMOKE_OK:4"


_SMOKE_RESULT = run_scene_pattern_catalog_io_smoke()
