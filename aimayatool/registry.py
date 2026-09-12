from __future__ import absolute_import


_GROUPS = (
    {"id": "skinning", "label": "Skinning", "module": "aimayatool.tools.skinning"},
    {"id": "setup", "label": "Setup", "module": "aimayatool.tools.setup"},
    {"id": "scene", "label": "Scene", "module": "aimayatool.tools.scene"},
)


def groups():
    return tuple(dict(item) for item in _GROUPS)
