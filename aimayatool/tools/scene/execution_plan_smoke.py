from __future__ import absolute_import

from .catalog import ScenePatternCatalog, ScenePatternEntry
from .execution_plan import build_scene_pattern_execution_plan


def run_scene_pattern_execution_plan_smoke():
    catalog = ScenePatternCatalog([
        ScenePatternEntry("global", "Scene_Pattern_Global", "global.json", order=2, title="Global", name="Global"),
        ScenePatternEntry("layer", "Scene_Pattern_Layer", "layer.json", order=1, title="Layer", name="Layer Main"),
    ])
    plan = build_scene_pattern_execution_plan(catalog)
    if [item["entry_id"] for item in plan] != ["layer", "global"]:
        raise AssertionError("Execution plan did not preserve deterministic catalog order.")
    if [item["callable"] for item in plan] != ["Run", "Run"]:
        raise AssertionError("Execution plan callable contract mismatch.")
    if plan[0]["module_name"] != "Scene_Pattern_Layer" or plan[0]["path"] != "layer.json":
        raise AssertionError("Execution plan lost module/path identity.")
    if catalog.get("layer").name != "Layer Main":
        raise AssertionError("Execution planning mutated catalog state.")

    type_rejected = False
    try:
        build_scene_pattern_execution_plan([])
    except TypeError:
        type_rejected = True
    if not type_rejected:
        raise AssertionError("Execution plan accepted a non-catalog input.")
    return "SCENE_PATTERN_EXECUTION_PLAN_SMOKE_OK:5"


_IMPORT_SMOKE_RESULT = run_scene_pattern_execution_plan_smoke()
