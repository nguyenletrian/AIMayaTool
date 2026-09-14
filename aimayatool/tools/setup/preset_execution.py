from __future__ import absolute_import

from . import controls, presets


def _cmds():
    import maya.cmds as cmds
    return cmds


def _preflight_scene(nodes, suffix):
    cmds = _cmds()
    missing = [node for node in nodes if not cmds.objExists(node)]
    if missing:
        raise ValueError("Source nodes do not exist: {0}".format(", ".join(missing)))
    outputs = []
    for node in nodes:
        short_name = node.split("|")[-1]
        output = short_name + suffix
        if cmds.objExists(output):
            raise ValueError("Control output already exists: {0}".format(output))
        outputs.append(output)
    return outputs


def create_controls_from_preset(nodes, preset, suffix=None):
    """Preflight a control-preset batch, then create matched controls in Maya."""
    request = presets.preflight_control_batch_request(nodes, preset)
    preset_data = request["preset"]
    if suffix is None:
        suffix = preset_data["suffix"]
    _preflight_scene(request["nodes"], suffix)
    return controls.create_controls_for_nodes(
        request["nodes"],
        shape=preset_data["shape"],
        size=preset_data["size"],
        suffix=suffix,
    )
