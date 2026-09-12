from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from aimayatool.registry import groups


WINDOW = "AIMayaToolWindow"


def _load_group(group):
    module = importlib.import_module(group["module"])
    build_ui = getattr(module, "build_ui", None)
    if build_ui:
        build_ui()
    else:
        cmds.text(label="{} tools are not migrated yet.".format(group["label"]))


def show():
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)

    cmds.window(WINDOW, title="AI Maya Tool", sizeable=True, widthHeight=(420, 680))
    root = cmds.scrollLayout(childResizable=True)
    cmds.columnLayout(parent=root, adjustableColumn=True, rowSpacing=4)

    for group in groups():
        cmds.frameLayout(label=group["label"], collapsable=True, collapse=False, marginWidth=6, marginHeight=6)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        _load_group(group)
        cmds.setParent("..")
        cmds.setParent("..")

    cmds.showWindow(WINDOW)
    return WINDOW
