from __future__ import absolute_import

from .compare_edit import apply_pattern_changes, compare_patterns

from .build_pipeline import BuildStep, run_build_pipeline
from .build_actions import build_scene_structure, ensure_group, ensure_hierarchy, parent_nodes
from .display_layers import add_members, ensure_display_layer, members, remove_members, set_display_type, set_visibility
from .operations import create_pattern, edit_pattern, load_pattern, save_pattern
from .presets import PresetLibrary
from .patterns import PatternRegistry, ScenePattern

REGISTRY = PatternRegistry()

def build_ui():
    import maya.cmds as cmds
    from aimayatool.ui.components import section

    column = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)
    section("Scene 2.0", spacing=False)
    cmds.separator(style="in", height=8)
    section("Patterns & Presets", "Create, edit, save, and organize reusable ScenePattern presets.", spacing=False)
    section("Compare & Edit", "Inspect deterministic field changes and apply validated partial edits.", spacing=False)
    section("Build Pipeline", "Run ordered reusable build steps with explicit error handling.", spacing=False)
    section("Display Layers", "Reusable display-layer helpers remain available through the Scene API.", spacing=False)
    return column

__all__ = [
    "BuildStep",
    "run_build_pipeline",
    "apply_pattern_changes",
    "compare_patterns",
    "PresetLibrary",
    "PatternRegistry",
    "REGISTRY",
    "ScenePattern",
    "add_members",
    "build_scene_structure",
    "build_ui",
    "create_pattern",
    "edit_pattern",
    "ensure_display_layer",
    "ensure_group",
    "ensure_hierarchy",
    "load_pattern",
    "members",
    "parent_nodes",
    "remove_members",
    "save_pattern",
    "set_display_type",
    "set_visibility",
]
