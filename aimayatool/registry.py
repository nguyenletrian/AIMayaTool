from __future__ import absolute_import

_GROUPS = (
    {"id": "skinning", "label": "Skinning", "module": "aimayatool.tools.skinning", "keywords": ("skin", "weights", "influences", "paint", "proxy")},
    {"id": "setup", "label": "Setup", "module": "aimayatool.tools.setup", "keywords": ("rig", "controls", "constraints", "ik", "fk", "spaces", "joints")},
    {"id": "scene", "label": "Scene", "module": "aimayatool.tools.scene", "keywords": ("scene", "patterns", "presets", "compare", "build", "layers")},
)

def groups():
    return tuple(dict(item) for item in _GROUPS)

def search_groups(query):
    text = (query or "").strip().lower()
    if not text:
        return groups()
    matches = []
    for item in _GROUPS:
        haystack = (item["id"], item["label"], item["module"]) + tuple(item.get("keywords", ()))
        if any(text in str(value).lower() for value in haystack):
            matches.append(dict(item))
    return tuple(matches)

_RECENT = []
_FAVORITES = set()

def mark_recent(group_id, limit=5):
    ids = tuple(item["id"] for item in _GROUPS)
    if group_id not in ids:
        raise ValueError("Unknown group: {0}".format(group_id))
    if group_id in _RECENT:
        _RECENT.remove(group_id)
    _RECENT.insert(0, group_id)
    del _RECENT[max(1, int(limit)):]
    return recent_groups()

def recent_groups():
    lookup = {item["id"]: item for item in _GROUPS}
    return tuple(dict(lookup[group_id]) for group_id in _RECENT if group_id in lookup)

def set_favorite(group_id, enabled=True):
    ids = tuple(item["id"] for item in _GROUPS)
    if group_id not in ids:
        raise ValueError("Unknown group: {0}".format(group_id))
    if enabled:
        _FAVORITES.add(group_id)
    else:
        _FAVORITES.discard(group_id)
    return favorite_groups()

def favorite_groups():
    return tuple(dict(item) for item in _GROUPS if item["id"] in _FAVORITES)
