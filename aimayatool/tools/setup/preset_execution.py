from __future__ import absolute_import

from . import controls, presets


def create_controls_from_preset(nodes, preset, suffix=None):
    """Preflight a control-preset batch, then create matched controls in Maya."""
    request = presets.preflight_control_batch(nodes, preset)
    preset_data = request["preset"]
    if suffix is None:
        suffix = preset_data["suffix"]
    return controls.create_controls_for_nodes(
        request["nodes"],
        shape=preset_data["shape"],
        size=preset_data["size"],
        suffix=suffix,
    )
