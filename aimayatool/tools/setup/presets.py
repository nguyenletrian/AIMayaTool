from __future__ import absolute_import

from . import controls


CONTROL_PRESET_VERSION = 1

_BUILTIN_CONTROL_PRESETS = {
    "fk": {"name": "fk", "shape": "circle", "size": 1.0, "suffix": "_CTRL"},
    "ik": {"name": "ik", "shape": "box", "size": 1.0, "suffix": "_CTRL"},
    "pole": {"name": "pole", "shape": "locator", "size": 1.0, "suffix": "_CTRL"},
}


def _require_text(value, label, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError("{0} must be a string.".format(label))
    value = value.strip()
    if not allow_empty and not value:
        raise ValueError("{0} must not be empty.".format(label))
    return value


def normalize_control_preset(preset):
    """Return a validated, canonical control preset without touching Maya."""
    if not isinstance(preset, dict):
        raise ValueError("Control preset must be a dictionary.")
    allowed = {"version", "name", "shape", "size", "suffix"}
    unknown = sorted(set(preset).difference(allowed))
    if unknown:
        raise ValueError("Unsupported control preset fields: {0}".format(", ".join(unknown)))
    version = int(preset.get("version", CONTROL_PRESET_VERSION))
    if version != CONTROL_PRESET_VERSION:
        raise ValueError("Unsupported control preset version: {0}".format(version))
    name = _require_text(preset.get("name", "control"), "Preset name")
    shape = _require_text(preset.get("shape", "circle"), "Control shape").lower()
    if shape not in controls.available_shapes():
        raise ValueError("Unsupported control shape: {0}".format(shape))
    try:
        size = float(preset.get("size", 1.0))
    except (TypeError, ValueError):
        raise ValueError("Control size must be numeric.")
    if size <= 0.0:
        raise ValueError("Control size must be greater than zero.")
    suffix = _require_text(preset.get("suffix", "_CTRL"), "Control suffix", allow_empty=True)
    return {"version": version, "name": name, "shape": shape, "size": size, "suffix": suffix}


def builtin_control_presets():
    """Return validated copies of the built-in reusable control presets."""
    return {name: normalize_control_preset(dict(data)) for name, data in sorted(_BUILTIN_CONTROL_PRESETS.items())}


def get_control_preset(name):
    key = _require_text(name, "Preset name").lower()
    try:
        data = _BUILTIN_CONTROL_PRESETS[key]
    except KeyError:
        raise ValueError("Unknown control preset: {0}".format(name))
    return normalize_control_preset(dict(data))


def preflight_control_batch_request(nodes, preset):
    """Validate one batch control-creation request before any Maya mutation."""
    normalized = normalize_control_preset(preset)
    nodes = list(nodes or [])
    if not nodes:
        raise ValueError("At least one source node is required.")
    cleaned = []
    seen = set()
    for index, node in enumerate(nodes):
        value = _require_text(node, "Source node {0}".format(index + 1))
        if value in seen:
            raise ValueError("Duplicate source node is not allowed: {0}".format(value))
        seen.add(value)
        cleaned.append(value)
    return {"nodes": cleaned, "preset": normalized, "count": len(cleaned)}
