from __future__ import absolute_import

import importlib

import maya.cmds as cmds

from aimayatool import registry


WINDOW = "AIMayaToolWindow"
_SEARCH = "AIMayaToolSearchField"
_TABS = "AIMayaToolTabs"
_TAB_BY_GROUP = {}
_DISCOVERY = "AIMayaToolDiscovery"


def _current_registry():
    global registry
    if not hasattr(registry, "search_groups"):
        registry = importlib.reload(registry)
    return registry


def _select_group(group_id):
    page = _TAB_BY_GROUP.get(group_id)
    if page:
        cmds.tabLayout(_TABS, edit=True, selectTab=page)
        _current_registry().mark_recent(group_id)
        _refresh_discovery()
    return page


def _refresh_discovery():
    if not cmds.text(_DISCOVERY, exists=True):
        return
    reg = _current_registry()
    recent = ", ".join(item["label"] for item in reg.recent_groups()) or "None"
    favorites = ", ".join(item["label"] for item in reg.favorite_groups()) or "None"
    cmds.text(_DISCOVERY, edit=True, label="Recent: {0}    Favorites: {1}".format(recent, favorites))


def _toggle_current_favorite(*_):
    selected = cmds.tabLayout(_TABS, query=True, selectTab=True)
    selected_short = selected.rsplit("|", 1)[-1]
    for group_id, page in _TAB_BY_GROUP.items():
        if page.rsplit("|", 1)[-1] == selected_short:
            reg = _current_registry()
            enabled = group_id not in tuple(item["id"] for item in reg.favorite_groups())
            reg.set_favorite(group_id, enabled)
            _refresh_discovery()
            return group_id


def _apply_search(*_):
    query = cmds.textField(_SEARCH, query=True, text=True)
    matches = _current_registry().search_groups(query)
    if matches:
        page = _TAB_BY_GROUP.get(matches[0]["id"])
        if page:
            _select_group(matches[0]["id"])
    return tuple(item["id"] for item in matches)


def search_interaction_smoke():
    show()
    expected = (("skin", "skinning"), ("rig", "setup"), ("preset", "scene"))
    for query, group_id in expected:
        cmds.textField(_SEARCH, edit=True, text=query)
        matches = _apply_search()
        selected = cmds.tabLayout(_TABS, query=True, selectTab=True)
        target = _TAB_BY_GROUP[group_id]
        selected_short = selected.rsplit("|", 1)[-1]
        target_short = target.rsplit("|", 1)[-1]
        if not matches or matches[0] != group_id or selected_short != target_short:
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
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, parent=root)
    cmds.text(_DISCOVERY, label="Recent: None    Favorites: None", align="left")
    cmds.button(label="Toggle Favorite", command=_toggle_current_favorite)
    cmds.setParent("..")
    tabs = cmds.tabLayout(_TABS, parent=root, innerMarginWidth=6, innerMarginHeight=6)

    _TAB_BY_GROUP.clear()
    tab_children = []
    for group in _current_registry().groups():
        page = cmds.scrollLayout(parent=tabs, childResizable=True)
        cmds.columnLayout(parent=page, adjustableColumn=True, rowSpacing=4)
        _load_group(group)
        cmds.setParent("..")
        cmds.setParent("..")
        _TAB_BY_GROUP[group["id"]] = page
        tab_children.append((page, group["label"]))

    cmds.tabLayout(tabs, edit=True, tabLabel=tab_children)
    _refresh_discovery()

    cmds.showWindow(WINDOW)
    return WINDOW
