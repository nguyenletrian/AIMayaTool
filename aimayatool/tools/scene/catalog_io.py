from __future__ import absolute_import

import io
import json
import os

from .catalog import ScenePatternCatalog


def save_catalog(catalog, path, overwrite=False):
    """Serialize a ScenePatternCatalog to UTF-8 JSON and return the absolute path."""
    if not isinstance(catalog, ScenePatternCatalog):
        raise TypeError("catalog must be a ScenePatternCatalog")
    path = os.path.abspath(os.path.expanduser(str(path)))
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        raise IOError("Parent directory does not exist: {0}".format(parent))
    if os.path.exists(path) and not overwrite:
        raise IOError("Catalog file already exists: {0}".format(path))
    with io.open(path, "w", encoding="utf-8") as stream:
        json.dump(catalog.to_dict(), stream, indent=2, sort_keys=True)
        stream.write("\n")
    return path


def load_catalog(path):
    """Load and validate a ScenePatternCatalog from a UTF-8 JSON file."""
    path = os.path.abspath(os.path.expanduser(str(path)))
    with io.open(path, "r", encoding="utf-8") as stream:
        return ScenePatternCatalog.from_dict(json.load(stream))
