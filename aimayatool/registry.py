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
_RECENT_ACTIONS = []
_FAVORITE_ACTIONS = set()
_ACTIONS = {}

def _require_group(group_id):
    if group_id not in tuple(item["id"] for item in _GROUPS):
        raise ValueError("Unknown group: {0}".format(group_id))
    return group_id

def _action_identity(group_id, action_id, label):
    _require_group(group_id)
    action_id = str(action_id or "").strip()
    label = str(label or "").strip()
    if not action_id:
        raise ValueError("Action id is required.")
    if not label:
        raise ValueError("Action label is required.")
    return {"group_id": group_id, "action_id": action_id, "label": label}

def _action_key(action):
    return (action["group_id"], action["action_id"])

def _remember_action(group_id, action_id, label):
    action = _action_identity(group_id, action_id, label)
    key = _action_key(action)
    existing = _ACTIONS.get(key)
    if existing is not None and existing["label"] != action["label"]:
        raise ValueError("Action label changed for {0}:{1}.".format(group_id, action_id))
    _ACTIONS[key] = action
    return action

def mark_recent(group_id, limit=5):
    _require_group(group_id)
    if group_id in _RECENT:
        _RECENT.remove(group_id)
    _RECENT.insert(0, group_id)
    del _RECENT[max(1, int(limit)):]
    return recent_groups()

def recent_groups():
    lookup = {item["id"]: item for item in _GROUPS}
    return tuple(dict(lookup[group_id]) for group_id in _RECENT if group_id in lookup)

def set_favorite(group_id, enabled=True):
    _require_group(group_id)
    if enabled:
        _FAVORITES.add(group_id)
    else:
        _FAVORITES.discard(group_id)
    return favorite_groups()

def favorite_groups():
    return tuple(dict(item) for item in _GROUPS if item["id"] in _FAVORITES)

def mark_recent_action(group_id, action_id, label, limit=5):
    action = _remember_action(group_id, action_id, label)
    key = _action_key(action)
    if key in _RECENT_ACTIONS:
        _RECENT_ACTIONS.remove(key)
    _RECENT_ACTIONS.insert(0, key)
    del _RECENT_ACTIONS[max(1, int(limit)):]
    return recent_actions()

def recent_actions():
    return tuple(dict(_ACTIONS[key]) for key in _RECENT_ACTIONS if key in _ACTIONS)

def set_favorite_action(group_id, action_id, label, enabled=True):
    action = _remember_action(group_id, action_id, label)
    key = _action_key(action)
    if enabled:
        _FAVORITE_ACTIONS.add(key)
    else:
        _FAVORITE_ACTIONS.discard(key)
    return favorite_actions()

def favorite_actions():
    ordered = sorted(_FAVORITE_ACTIONS)
    return tuple(dict(_ACTIONS[key]) for key in ordered if key in _ACTIONS)
