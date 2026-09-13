from __future__ import absolute_import

from .operations import create_pattern, edit_pattern, load_pattern, save_pattern
from .patterns import PatternRegistry, ScenePattern


REGISTRY = PatternRegistry()


def build_ui():
    import maya.cmds as cmds

    cmds.text(label="Scene Patterns", align="left")
    cmds.text(label="Create, load, edit, and save deterministic ScenePattern data.", align="left")


__all__ = [
    "PatternRegistry",
    "REGISTRY",
    "ScenePattern",
    "build_ui",
    "create_pattern",
    "edit_pattern",
    "load_pattern",
    "save_pattern",
]
