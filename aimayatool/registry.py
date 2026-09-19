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
