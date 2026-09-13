from __future__ import absolute_import

from .display_layers import add_members, ensure_display_layer, members, remove_members, set_display_type, set_visibility
from .operations import create_pattern, edit_pattern, load_pattern, save_pattern
from .patterns import PatternRegistry, ScenePattern


REGISTRY = PatternRegistry()


def build_ui():
    import maya.cmds as cmds

    cmds.text(label="Scene Patterns", align="left")
    cmds.text(label="Create, load, edit, and save deterministic ScenePattern data.", align="left")
    cmds.text(label="Reusable display-layer helpers are available through the Scene API.", align="left")


__all__ = [
    "PatternRegistry",
    "REGISTRY",
    "ScenePattern",
    "add_members",
    "build_ui",
    "create_pattern",
    "edit_pattern",
    "ensure_display_layer",
    "load_pattern",
    "members",
    "remove_members",
    "save_pattern",
    "set_display_type",
    "set_visibility",
]
