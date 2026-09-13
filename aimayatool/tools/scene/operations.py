from __future__ import absolute_import

import io
import os

from .patterns import ScenePattern


_UNSET = object()


def create_pattern(pattern_id, label=None, nodes=None, metadata=None):
    """Create a validated ScenePattern from explicit values."""
    return ScenePattern(pattern_id, label=label, nodes=nodes, metadata=metadata)


def edit_pattern(pattern, pattern_id=_UNSET, label=_UNSET, nodes=_UNSET, metadata=_UNSET):
    """Return an edited copy without mutating the source ScenePattern."""
    if not isinstance(pattern, ScenePattern):
        raise TypeError("pattern must be a ScenePattern")
    return ScenePattern(
        pattern.pattern_id if pattern_id is _UNSET else pattern_id,
        label=pattern.label if label is _UNSET else label,
        nodes=pattern.nodes if nodes is _UNSET else nodes,
        metadata=pattern.metadata if metadata is _UNSET else metadata,
    )


def save_pattern(pattern, path, overwrite=False):
    """Serialize a ScenePattern to UTF-8 JSON and return the absolute path."""
    if not isinstance(pattern, ScenePattern):
        raise TypeError("pattern must be a ScenePattern")
    path = os.path.abspath(os.path.expanduser(str(path)))
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        raise IOError("Parent directory does not exist: {0}".format(parent))
    if os.path.exists(path) and not overwrite:
        raise IOError("Pattern file already exists: {0}".format(path))
    with io.open(path, "w", encoding="utf-8") as stream:
        stream.write(pattern.to_json(indent=2))
        stream.write("\n")
    return path


def load_pattern(path):
    """Load and validate a ScenePattern from a UTF-8 JSON file."""
    path = os.path.abspath(os.path.expanduser(str(path)))
    with io.open(path, "r", encoding="utf-8") as stream:
        return ScenePattern.from_json(stream.read())
