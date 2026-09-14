from __future__ import absolute_import

from .catalog import ScenePatternCatalog, ScenePatternEntry


def run_scene_pattern_catalog_smoke():
    first = ScenePatternEntry("b", "Scene_Pattern_Global", "global.json", order=2, title="Global", name="Global 2")
    second = ScenePatternEntry("a", "Scene_Pattern_Layer", "layer.json", order=1, title="Layer", name="Layer")
    catalog = ScenePatternCatalog([first, second])
    if [entry.entry_id for entry in catalog.ordered()] != ["a", "b"]:
        raise AssertionError("Catalog ordering is not deterministic.")

    renamed = catalog.rename("a", "Layer Main")
    if renamed.name != "Layer Main" or second.name != "Layer":
        raise AssertionError("Catalog rename must replace the entry without mutating the source object.")

    reordered = catalog.reorder("b", 0)
    if reordered.order != 0 or [entry.entry_id for entry in catalog.ordered()] != ["b", "a"]:
        raise AssertionError("Catalog reorder failed.")

    restored = ScenePatternCatalog.from_dict(catalog.to_dict())
    if restored.to_dict() != catalog.to_dict():
        raise AssertionError("Catalog serialization round trip failed.")

    duplicate_rejected = False
    try:
        catalog.add(first)
    except ValueError:
        duplicate_rejected = True
    if not duplicate_rejected:
        raise AssertionError("Duplicate ScenePattern entry was not rejected.")

    removed = catalog.remove("a")
    if removed is None or catalog.get("a") is not None:
        raise AssertionError("Catalog remove failed.")
    return "SCENE_PATTERN_CATALOG_SMOKE_OK:6"


SMOKE_RESULT = run_scene_pattern_catalog_smoke()
