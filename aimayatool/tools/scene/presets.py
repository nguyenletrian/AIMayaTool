from __future__ import absolute_import

import os

from .operations import load_pattern, save_pattern
from .patterns import ScenePattern


class PresetLibrary(object):
    """Deterministic filesystem-backed library for ScenePattern presets."""

    def __init__(self, root):
        self.root = os.path.abspath(os.path.expanduser(str(root)))

    def _name(self, name):
        name = str(name or "").strip()
        if not name or name in (".", "..") or os.path.basename(name) != name or "/" in name or "\\\\" in name:
            raise ValueError("Invalid preset name: {0}".format(name))
        return name[:-5] if name.lower().endswith(".json") else name

    def path(self, name):
        name = self._name(name)
        path = os.path.abspath(os.path.join(self.root, name + ".json"))
        if os.path.commonpath([self.root, path]) != self.root:
            raise ValueError("Preset path escapes library root")
        return path

    def list(self):
        if not os.path.isdir(self.root):
            return []
        return sorted(os.path.splitext(name)[0] for name in os.listdir(self.root) if name.lower().endswith(".json") and os.path.isfile(os.path.join(self.root, name)))

    def get(self, name):
        path = self.path(name)
        if not os.path.isfile(path):
            return None
        return load_pattern(path)

    def save(self, name, pattern, overwrite=False):
        if not isinstance(pattern, ScenePattern):
            raise TypeError("pattern must be a ScenePattern")
        if not os.path.isdir(self.root):
            os.makedirs(self.root)
        return save_pattern(pattern, self.path(name), overwrite=overwrite)

    def delete(self, name, missing_ok=False):
        path = self.path(name)
        if not os.path.isfile(path):
            if missing_ok:
                return False
            raise IOError("Preset does not exist: {0}".format(path))
        os.remove(path)
        return True
