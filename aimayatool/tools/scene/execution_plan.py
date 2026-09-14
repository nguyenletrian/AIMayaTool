from __future__ import absolute_import

from .catalog import ScenePatternCatalog


def build_scene_pattern_execution_plan(catalog):
    """Return an ordered, host-independent run plan from a ScenePatternCatalog.

    The plan describes what legacy Scene.RunItem used to resolve dynamically without
    importing modules or mutating Maya state. Host adapters may later consume this
    validated data and decide how to resolve/execute modules.
    """
    if not isinstance(catalog, ScenePatternCatalog):
        raise TypeError("catalog must be a ScenePatternCatalog")
    plan = []
    seen_ids = set()
    for entry in catalog.ordered():
        if entry.entry_id in seen_ids:
            raise ValueError("Duplicate ScenePattern entry in execution plan: {0}".format(entry.entry_id))
        seen_ids.add(entry.entry_id)
        module_name = str(entry.module_name or "").strip()
        path = str(entry.path or "").strip()
        if not module_name:
            raise ValueError("ScenePattern module_name is required: {0}".format(entry.entry_id))
        if not path:
            raise ValueError("ScenePattern path is required: {0}".format(entry.entry_id))
        plan.append({
            "entry_id": entry.entry_id,
            "module_name": module_name,
            "path": path,
            "order": entry.order,
            "title": entry.title,
            "name": entry.name,
            "callable": "Run",
        })
    return tuple(plan)
