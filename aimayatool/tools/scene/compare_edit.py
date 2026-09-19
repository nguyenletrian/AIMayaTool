from __future__ import absolute_import

from .patterns import ScenePattern

_FIELDS = ("pattern_id", "label", "nodes", "metadata")


def compare_patterns(before, after):
    """Return a deterministic field-level diff between two ScenePatterns."""
    if not isinstance(before, ScenePattern) or not isinstance(after, ScenePattern):
        raise TypeError("before and after must be ScenePattern instances")
    changes = []
    for field in _FIELDS:
        old = getattr(before, field)
        new = getattr(after, field)
        if old != new:
            changes.append({"field": field, "before": old, "after": new})
    return {"changed": bool(changes), "changes": changes}


def apply_pattern_changes(pattern, changes):
    """Apply explicit field changes through the existing immutable edit API."""
    if not isinstance(pattern, ScenePattern):
        raise TypeError("pattern must be a ScenePattern")
    if not isinstance(changes, dict):
        raise TypeError("changes must be a dictionary")
    unknown = sorted(set(changes) - set(_FIELDS))
    if unknown:
        raise ValueError("Unsupported pattern fields: {0}".format(", ".join(unknown)))
    from .operations import edit_pattern
    return edit_pattern(pattern, **changes)
