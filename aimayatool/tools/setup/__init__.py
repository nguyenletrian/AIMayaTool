from __future__ import absolute_import

import maya.cmds as cmds

from .controls import create_controls_for_nodes, create_zero_group


def _selected_transforms():
    return cmds.ls(selection=True, long=True, type="transform") or []


def _create_selected(shape):
    nodes = _selected_transforms()
    if not nodes:
        cmds.warning("Select one or more transforms to create matched controls.")
        return []
    controls = create_controls_for_nodes(nodes, shape=shape)
    cmds.select(controls, replace=True)
    return controls


def _zero_selected():
    nodes = _selected_transforms()
    if not nodes:
        cmds.warning("Select one or more controls/transforms to zero-group.")
        return []
    groups = [create_zero_group(node)[0] for node in nodes]
    cmds.select(groups, replace=True)
    return groups


def build_ui():
    cmds.text(label="Controls", align="left")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    cmds.button(label="Circle", command=lambda *_: _create_selected("circle"))
    cmds.button(label="Box", command=lambda *_: _create_selected("box"))
    cmds.button(label="Zero Group", command=lambda *_: _zero_selected())
    cmds.setParent("..")
