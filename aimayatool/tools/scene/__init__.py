from __future__ import absolute_import

import maya.cmds as cmds

from .patterns import PatternRegistry, ScenePattern


REGISTRY = PatternRegistry()


def build_ui():
    cmds.text(label="Scene Patterns", align="left")
    cmds.text(label="Deterministic ScenePattern model and registry ready.", align="left")


__all__ = ["PatternRegistry", "REGISTRY", "ScenePattern", "build_ui"]
