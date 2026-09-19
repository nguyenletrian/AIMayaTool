from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from aimayatool import registry


WINDOW = "AIMayaToolWindow"
_SEARCH = "AIMayaToolSearchField"
_TABS = "AIMayaToolTabs"
_TAB_BY_GROUP = {}


def _apply_search(*_):
    query = cmds.textField(_SEARCH, query=True, text=True)
    matches = registry.search_groups(query)
    if matches:
        page = _TAB_BY_GROUP.get(matches[0]["id"])
        if page:
            cmds.tabLayout(_TABS, edit=True, selectTab=page)
    return tuple(item["id"] for item in matches)


def search_interaction_smoke():
    show()
    expected = (("skin", "skinning"), ("rig", "setup"), ("preset", "scene"))
    for query, group_id in expected:
        cmds.textField(_SEARCH, edit=True, text=query)
        matches = _apply_search()
        selected = cmds.tabLayout(_TABS, query=True, selectTab=True)
        target = _TAB_BY_GROUP[group_id]
        if not matches or matches[0] != group_id or selected != target:
            raise RuntimeError("Search failed for {0}: {1}, selected={2}, target={3}".format(query, matches, selected, target))
    return "AIBRIDGE_UI_SEARCH_OK:" + "|".join(item[1] for item in expected)


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
    cmds.textField(_SEARCH, parent=root, placeholderText="Search Skinning, Setup, Scene...", changeCommand=_apply_search, enterCommand=_apply_search)
    tabs = cmds.tabLayout(_TABS, parent=root, innerMarginWidth=6, innerMarginHeight=6)

    _TAB_BY_GROUP.clear()
    tab_children = []
    for group in registry.groups():
        page = cmds.scrollLayout(parent=tabs, childResizable=True)
        cmds.columnLayout(parent=page, adjustableColumn=True, rowSpacing=4)
        _load_group(group)
        cmds.setParent("..")
        cmds.setParent("..")
        _TAB_BY_GROUP[group["id"]] = page
        tab_children.append((page, group["label"]))

    cmds.tabLayout(tabs, edit=True, tabLabel=tab_children)

    cmds.showWindow(WINDOW)
    return WINDOW
