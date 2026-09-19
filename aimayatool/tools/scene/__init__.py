from .compare_edit import apply_pattern_changes, compare_patterns
from __future__ import absolute_import

from .build_actions import build_scene_structure, ensure_group, ensure_hierarchy, parent_nodes
from .display_layers import add_members, ensure_display_layer, members, remove_members, set_display_type, set_visibility
from .operations import create_pattern, edit_pattern, load_pattern, save_pattern
from .presets import PresetLibrary
from .patterns import PatternRegistry, ScenePattern


REGISTRY = PatternRegistry()


def build_ui():
    import maya.cmds as cmds

    cmds.text(label="Scene Patterns", align="left")
    cmds.text(label="Create, load, edit, and save deterministic ScenePattern data.", align="left")
    cmds.text(label="Reusable display-layer and scene build helpers are available through the Scene API.", align="left")


__all__ = [
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
