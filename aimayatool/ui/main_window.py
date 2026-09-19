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
    root = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)
    tabs = cmds.tabLayout(parent=root, innerMarginWidth=6, innerMarginHeight=6)

    tab_children = []
    for group in groups():
        page = cmds.scrollLayout(parent=tabs, childResizable=True)
        cmds.columnLayout(parent=page, adjustableColumn=True, rowSpacing=4)
        _load_group(group)
        cmds.setParent("..")
        cmds.setParent("..")
        tab_children.append((page, group["label"]))

    cmds.tabLayout(tabs, edit=True, tabLabel=tab_children)

    cmds.showWindow(WINDOW)
    return WINDOW
