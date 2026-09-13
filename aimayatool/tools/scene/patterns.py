from __future__ import absolute_import

import json


class ScenePattern(object):
    """Small deterministic description of a reusable scene pattern."""

    VERSION = 1

    def __init__(self, pattern_id, label=None, nodes=None, metadata=None):
        pattern_id = str(pattern_id or "").strip()
        if not pattern_id:
            raise ValueError("pattern_id is required")
        self.pattern_id = pattern_id
        self.label = str(label or pattern_id)
        self.nodes = list(nodes or [])
        self.metadata = dict(metadata or {})

    def to_dict(self):
        return {
            "version": self.VERSION,
            "pattern_id": self.pattern_id,
            "label": self.label,
            "nodes": list(self.nodes),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("ScenePattern data must be a dictionary")
        version = data.get("version", cls.VERSION)
        if version != cls.VERSION:
            raise ValueError("Unsupported ScenePattern version: {0}".format(version))
        return cls(
            pattern_id=data.get("pattern_id"),
            label=data.get("label"),
            nodes=data.get("nodes") or [],
            metadata=data.get("metadata") or {},
        )

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(text))


class PatternRegistry(object):
    """In-memory registry with explicit duplicate handling."""

    def __init__(self):
        self._patterns = {}

    def register(self, pattern, replace=False):
        if not isinstance(pattern, ScenePattern):
            raise TypeError("pattern must be a ScenePattern")
        if pattern.pattern_id in self._patterns and not replace:
            raise ValueError("Pattern already registered: {0}".format(pattern.pattern_id))
        self._patterns[pattern.pattern_id] = pattern
        return pattern

    def get(self, pattern_id):
        return self._patterns.get(pattern_id)

    def remove(self, pattern_id):
        return self._patterns.pop(pattern_id, None)

    def ids(self):
        return sorted(self._patterns)

    def clear(self):
        self._patterns.clear()
