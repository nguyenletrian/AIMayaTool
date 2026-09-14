from __future__ import absolute_import


class ScenePatternEntry(object):
    """One ordered ScenePattern catalog entry with explicit immutable identity."""

    VERSION = 1

    def __init__(self, entry_id, module_name, path, order=0, title=None, name=None):
        entry_id = str(entry_id or "").strip()
        module_name = str(module_name or "").strip()
        path = str(path or "").strip()
        if not entry_id:
            raise ValueError("entry_id is required")
        if not module_name:
            raise ValueError("module_name is required")
        if not path:
            raise ValueError("path is required")
        if isinstance(order, bool) or not isinstance(order, int):
            raise TypeError("order must be an integer")
        self.entry_id = entry_id
        self.module_name = module_name
        self.path = path
        self.order = order
        self.title = str(title or module_name)
        self.name = str(name or self.title)

    def to_dict(self):
        return {
            "version": self.VERSION,
            "id": self.entry_id,
            "module_name": self.module_name,
            "path": self.path,
            "order": self.order,
            "title": self.title,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("ScenePatternEntry data must be a dictionary")
        version = data.get("version", cls.VERSION)
        if version != cls.VERSION:
            raise ValueError("Unsupported ScenePatternEntry version: {0}".format(version))
        return cls(
            data.get("id"),
            data.get("module_name"),
            data.get("path"),
            order=data.get("order", 0),
            title=data.get("title"),
            name=data.get("name"),
        )

    def copy(self, **changes):
        values = self.to_dict()
        values.update(changes)
        return ScenePatternEntry.from_dict(values)


class ScenePatternCatalog(object):
    """Deterministic ordered catalog for ScenePattern entries."""

    VERSION = 1

    def __init__(self, entries=None):
        self._entries = {}
        for entry in entries or []:
            self.add(entry)

    def add(self, entry, replace=False):
        if not isinstance(entry, ScenePatternEntry):
            raise TypeError("entry must be a ScenePatternEntry")
        if entry.entry_id in self._entries and not replace:
            raise ValueError("ScenePattern entry already exists: {0}".format(entry.entry_id))
        self._entries[entry.entry_id] = entry
        return entry

    def get(self, entry_id):
        return self._entries.get(entry_id)

    def remove(self, entry_id):
        return self._entries.pop(entry_id, None)

    def ordered(self):
        return tuple(sorted(self._entries.values(), key=lambda entry: (entry.order, entry.entry_id)))

    def reorder(self, entry_id, order):
        entry = self.get(entry_id)
        if entry is None:
            raise KeyError("Unknown ScenePattern entry: {0}".format(entry_id))
        updated = entry.copy(order=order)
        self._entries[entry_id] = updated
        return updated

    def rename(self, entry_id, name):
        entry = self.get(entry_id)
        if entry is None:
            raise KeyError("Unknown ScenePattern entry: {0}".format(entry_id))
        updated = entry.copy(name=name)
        self._entries[entry_id] = updated
        return updated

    def to_dict(self):
        return {"version": self.VERSION, "entries": [entry.to_dict() for entry in self.ordered()]}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("ScenePatternCatalog data must be a dictionary")
        version = data.get("version", cls.VERSION)
        if version != cls.VERSION:
            raise ValueError("Unsupported ScenePatternCatalog version: {0}".format(version))
        return cls(ScenePatternEntry.from_dict(item) for item in data.get("entries") or [])
