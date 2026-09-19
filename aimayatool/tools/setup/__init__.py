from __future__ import absolute_import

from .controls import create_controls_for_nodes, create_zero_group, replace_control_shape, available_shapes


def _cmds():
    import maya.cmds as cmds
    return cmds


def _selected_transforms():
    cmds = _cmds()
    return cmds.ls(selection=True, long=True, type="transform") or []


def _run(label, fn):
    from aimayatool.ui.components import run_action
    return run_action(label, fn, context="AIMayaTool Setup")

def _selection_context(minimum=1, usage="Select one or more transforms.", exact=None):
    """Return ordered transform selection with explicit count validation."""
    nodes = _selected_transforms()
    if exact is not None and len(nodes) != exact:
        raise ValueError(usage)
    if len(nodes) < minimum:
        raise ValueError(usage)
    return nodes


def _require_selection(minimum, usage):
    return _selection_context(minimum=minimum, usage=usage)


def selection_context_managed_maya_smoke():
    """Focused proof that selection context preserves order and fails without mutation."""
    cmds = _cmds()
    first = cmds.createNode("transform", name="AIMayaToolContextFirst")
    second = cmds.createNode("transform", name="AIMayaToolContextSecond")
    cmds.select(first, second, replace=True)
    expected = _selected_transforms()
    result = _selection_context(minimum=2, exact=2, usage="expected two")
    if result != expected:
        raise RuntimeError("Selection order changed: {0} != {1}".format(result, expected))
    before = cmds.ls(selection=True, long=True) or []
    try:
        _selection_context(minimum=3, usage="expected context failure")
    except ValueError as exc:
        if str(exc) != "expected context failure":
            raise
    else:
        raise RuntimeError("Expected minimum-count failure")
    after = cmds.ls(selection=True, long=True) or []
    if after != before:
        raise RuntimeError("Selection context mutated Maya selection")
    return "AIBRIDGE_CONTEXT_SELECTION_OK:ordered|nonmutating"


def _create_selected(shape):
    cmds = _cmds()
    nodes = _require_selection(1, "Select one or more transforms to create matched controls.")
    result = create_controls_for_nodes(nodes, shape=shape)
    cmds.select(result, replace=True)
    return result


def _replace_selected_shape():
    cmds = _cmds()
    nodes = _require_selection(1, "Select one or more curve controls to replace their shapes.")
    shapes = available_shapes()
    if cmds.promptDialog(title="Replace Control Shape", message="Shape ({0}):".format(", ".join(shapes)), button=["Apply", "Cancel"], defaultButton="Apply", cancelButton="Cancel", dismissString="Cancel") != "Apply":
        return []
    shape = cmds.promptDialog(query=True, text=True).strip().lower()
    if shape not in shapes:
        raise ValueError("Unsupported control shape: {0}".format(shape))
    return [replace_control_shape(node, shape=shape)[0] for node in nodes]


def _zero_selected():
    cmds = _cmds()
    nodes = _require_selection(1, "Select one or more controls/transforms to zero-group.")
    groups = [create_zero_group(node)[0] for node in nodes]
    cmds.select(groups, replace=True)
    return groups


def _freeze_selected():
    from . import transforms
    return transforms.freeze_transforms(_require_selection(1, "Select transforms to freeze."))


def _reset_selected():
    from . import transforms
    return transforms.reset_transforms(_require_selection(1, "Select transforms to reset."), translate=True, rotate=True, scale=False)


def batch_reset_managed_maya_smoke():
    """Prove ordered multi-selection Reset TR behavior without saving the scene."""
    cmds = _cmds()
    nodes = [cmds.createNode("transform", name="AIMayaToolBatchReset{0}".format(i)) for i in range(3)]
    for i, node in enumerate(nodes):
        cmds.setAttr(node + ".translateX", float(i + 2))
        cmds.setAttr(node + ".rotateY", float((i + 1) * 10))
        cmds.setAttr(node + ".scaleX", float(i + 2))
    cmds.select(nodes, replace=True)
    expected = cmds.ls(selection=True, long=True) or []
    import importlib
    from . import transforms
    importlib.reload(transforms)
    _reset_selected()
    actual = cmds.ls(selection=True, long=True) or []
    if actual != expected:
        raise RuntimeError("Selection order changed: {0} != {1}".format(actual, expected))
    for i, node in enumerate(nodes):
        if any(abs(cmds.getAttr(node + ".translate" + axis)) > 1e-6 for axis in "XYZ"):
            raise RuntimeError("Translation was not reset: {0}".format(node))
        if any(abs(cmds.getAttr(node + ".rotate" + axis)) > 1e-6 for axis in "XYZ"):
            raise RuntimeError("Rotation was not reset: {0}".format(node))
        if abs(cmds.getAttr(node + ".scaleX") - float(i + 2)) > 1e-6:
            raise RuntimeError("Scale was unexpectedly changed: {0}".format(node))
    return "AIBRIDGE_BATCH_RESET_OK:ordered|TR_reset|scale_preserved"


def _create_joints_selected():
    from . import transforms
    cmds = _cmds()
    result = transforms.create_joints_at_references(_require_selection(1, "Select transforms to create matched joints."))
    cmds.select(result, replace=True)
    return result


def _parent_constraint_selected():
    from . import constraints
    nodes = _require_selection(2, "Select one or more drivers, then the driven transform last.")
    return constraints.create_parent_constraint(nodes[:-1], nodes[-1])


def _point_constraint_selected():
    from . import constraints
    nodes = _require_selection(2, "Select driver first, then driven transform last.")
    return constraints.create_point_constraint(nodes[0], nodes[-1])


def _orient_constraint_selected():
    from . import constraints
    nodes = _require_selection(2, "Select driver first, then driven transform last.")
    return constraints.create_orient_constraint(nodes[0], nodes[-1])


def _aim_constraint_selected():
    from . import constraints
    nodes = _require_selection(3, "Select aim driver, driven transform, then world-up object.")
    return constraints.create_aim_constraint(nodes[0], nodes[1], nodes[2])


def _space_switch_selected():
    from . import spaces
    nodes = _require_selection(2, "Select one or more space parents, then the child control last.")
    return spaces.create_space_switch(nodes[-1], nodes[:-1])


def _copy_attribute_selected():
    from . import attributes
    cmds = _cmds()
    nodes = _require_selection(2, "Select source first, then one or more targets.")
    if cmds.promptDialog(title="Copy Attribute", message="Attribute name:", button=["Copy", "Cancel"], defaultButton="Copy", cancelButton="Cancel", dismissString="Cancel") != "Copy":
        return None
    attribute = cmds.promptDialog(query=True, text=True).strip()
    if not attribute:
        raise ValueError("Attribute name is required.")
    return attributes.copy_attribute_value(nodes[0], nodes[1:], attribute)


def _spline_ik_selected():
    from . import secondary
    nodes = _require_selection(2, "Select two or more transform references in chain order.")
    result = secondary.create_spline_ik_chain(nodes)
    _cmds().select(result["joints"], replace=True)
    return result


def _object_on_curve_selected():
    from . import secondary
    cmds = _cmds()
    selection = cmds.ls(selection=True, long=True) or []
    if len(selection) < 2:
        raise ValueError("Select the curve first, then one or more transforms to attach.")
    curve = selection[0]
    objects = [node for node in selection[1:] if cmds.nodeType(node) == "transform"]
    if not objects:
        raise ValueError("Select one or more transform objects after the curve.")
    return secondary.attach_objects_to_curve(curve, objects)


def _joints_between_selected():
    from . import secondary
    cmds = _cmds()
    nodes = _require_selection(2, "Select start transform first, then end transform.")
    if cmds.promptDialog(title="Joints Between", message="Interior joint count:", text="3", button=["Create", "Cancel"], defaultButton="Create", cancelButton="Cancel", dismissString="Cancel") != "Create":
        return []
    try:
        count = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("Interior joint count must be an integer.")
    result = secondary.create_joints_between(nodes[0], nodes[1], count)
    cmds.select(result, replace=True)
    return result


def _rp_ik_selected():
    from . import ikfk
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True) or []
    if len(nodes) < 4:
        raise ValueError("Select IK joints in chain order, then IK control, then pole control.")
    ik_control, pole_control = nodes[-2], nodes[-1]
    ik_joints = nodes[:-2]
    if len(ik_joints) < 2 or any(cmds.nodeType(node) != "joint" for node in ik_joints):
        raise ValueError("All selections before the final two controls must be joints in IK chain order.")
    result = ikfk.create_rp_ik(ik_joints, ik_control, pole_control)
    cmds.select(ik_control, pole_control, replace=True)
    return result


def _snap_ikfk_selected():
    from . import ikfk
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True, type="transform") or []
    if len(nodes) < 2 or len(nodes) % 2:
        raise ValueError("Select alternating source/target transform pairs: source, target, source, target...")
    if cmds.promptDialog(title="Snap IK/FK", message="Switch attribute (node.attr):", button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    switch_attr = cmds.promptDialog(query=True, text=True).strip()
    if not switch_attr:
        raise ValueError("Switch attribute is required.")
    if cmds.promptDialog(title="Snap IK/FK", message="Switch value:", text="1", button=["Snap", "Cancel"], defaultButton="Snap", cancelButton="Cancel", dismissString="Cancel") != "Snap":
        return None
    try:
        switch_value = float(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("Switch value must be numeric.")
    return ikfk.snap_ikfk(nodes[0::2], nodes[1::2], switch_attr, switch_value)


def _wire_ikfk_switch_selected():
    from . import ikfk
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True, type="transform") or []
    if len(nodes) < 2:
        raise ValueError("Select FK visibility nodes first, then IK visibility nodes, then optional proxy controls.")
    if cmds.promptDialog(title="Wire IK/FK Switch", message="Switch attribute (node.attr):", button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    switch_attr = cmds.promptDialog(query=True, text=True).strip()
    if not switch_attr:
        raise ValueError("Switch attribute is required.")
    if cmds.promptDialog(title="Wire IK/FK Switch", message="FK node count:", text="1", button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    try:
        fk_count = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("FK node count must be an integer.")
    if cmds.promptDialog(title="Wire IK/FK Switch", message="IK node count:", text="1", button=["Wire", "Cancel"], defaultButton="Wire", cancelButton="Cancel", dismissString="Cancel") != "Wire":
        return None
    try:
        ik_count = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("IK node count must be an integer.")
    if fk_count < 1 or ik_count < 1 or fk_count + ik_count > len(nodes):
        raise ValueError("FK/IK counts must be positive and fit within the current selection.")
    fk_nodes = nodes[:fk_count]
    ik_nodes = nodes[fk_count:fk_count + ik_count]
    proxy_nodes = nodes[fk_count + ik_count:]
    return ikfk.wire_ikfk_switch(switch_attr, fk_nodes, ik_nodes, proxy_nodes=proxy_nodes)


def _blend_ikfk_selected():
    from . import ikfk
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True) or []
    if len(nodes) < 3:
        raise ValueError("Select bind joints, then FK joints, then IK joints; all three chains must be equal length.")
    if cmds.promptDialog(title="Create IK/FK Blend", message="Switch attribute (node.attr):", button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    switch_attr = cmds.promptDialog(query=True, text=True).strip()
    if not switch_attr:
        raise ValueError("Switch attribute is required.")
    default_count = str(len(nodes) // 3) if len(nodes) % 3 == 0 else "1"
    if cmds.promptDialog(title="Create IK/FK Blend", message="Joints per chain:", text=default_count, button=["Create", "Cancel"], defaultButton="Create", cancelButton="Cancel", dismissString="Cancel") != "Create":
        return None
    try:
        count = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("Joints per chain must be an integer.")
    if count < 1 or len(nodes) != count * 3:
        raise ValueError("Selection must contain exactly three equal chains: bind, FK, IK.")
    if any(cmds.nodeType(node) != "joint" for node in nodes):
        raise ValueError("All IK/FK blend selections must be joints.")
    bind_joints = nodes[:count]
    fk_joints = nodes[count:count * 2]
    ik_joints = nodes[count * 2:]
    return ikfk.create_ikfk_blend(bind_joints, fk_joints, ik_joints, switch_attr)


def _secondary_driver_attr(cmds, title, driver_node):
    if cmds.promptDialog(title=title, message="Driver attribute name:", text="amount", button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    attribute = cmds.promptDialog(query=True, text=True).strip()
    if not attribute or "." in attribute:
        raise ValueError("Driver attribute must be a non-empty attribute name, not a node.attr plug.")
    return driver_node + "." + attribute


def _smart_group_count(total, fixed, fallback=1):
    """Suggest an equal paired-group count when selection shape is unambiguous."""
    remaining = total - fixed
    return remaining // 2 if remaining > 0 and remaining % 2 == 0 else fallback


def smart_group_count_managed_maya_smoke():
    """Focused proof for deterministic prompt default without scene mutation."""
    cmds = _cmds()
    before = cmds.ls(selection=True, long=True) or []
    cases = ((8, 4, 2), (6, 2, 2), (7, 4, 1), (4, 4, 1))
    for total, fixed, expected in cases:
        result = _smart_group_count(total, fixed)
        if result != expected:
            raise RuntimeError("Smart count mismatch: {0}, {1} -> {2}, expected {3}".format(total, fixed, result, expected))
    if _smart_group_count(7, 4, fallback=3) != 3:
        raise RuntimeError("Explicit fallback was not preserved")
    after = cmds.ls(selection=True, long=True) or []
    if after != before:
        raise RuntimeError("Smart count mutated Maya selection")
    return "AIBRIDGE_SMART_DEFAULT_OK:deterministic|override"


def _secondary_count(cmds, title, total, fixed):
    default_count = str(_smart_group_count(total, fixed))
    if cmds.promptDialog(title=title, message="Objects / destinations count:", text=default_count, button=["Next", "Cancel"], defaultButton="Next", cancelButton="Cancel", dismissString="Cancel") != "Next":
        return None
    try:
        count = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("Objects / destinations count must be an integer.")
    if count < 1 or total != fixed + count * 2:
        raise ValueError("Selection count does not match the requested object/destination count.")
    return count


def _fold_rig_selected():
    from . import secondary
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True) or []
    if len(nodes) < 4:
        raise ValueError("Select end target, objects, matching destinations, then driver node.")
    count = _secondary_count(cmds, "Create Fold Rig", len(nodes), 2)
    if count is None:
        return None
    driver_attr = _secondary_driver_attr(cmds, "Create Fold Rig", nodes[-1])
    if driver_attr is None:
        return None
    return secondary.create_fold_rig(nodes[1:1 + count], nodes[0], nodes[1 + count:1 + count * 2], driver_attr)


def _rope_selected(roll=False):
    from . import secondary
    cmds = _cmds()
    nodes = cmds.ls(selection=True, long=True) or []
    title = "Create Rope Roll" if roll else "Create Rope Straight"
    if len(nodes) < 6:
        raise ValueError("Select start target, end target, objects, matching destinations, orient reference, then driver node.")
    count = _secondary_count(cmds, title, len(nodes), 4)
    if count is None:
        return None
    driver_attr = _secondary_driver_attr(cmds, title, nodes[-1])
    if driver_attr is None:
        return None
    if cmds.promptDialog(title=title, message="Offset:", text="0", button=["Create", "Cancel"], defaultButton="Create", cancelButton="Cancel", dismissString="Cancel") != "Create":
        return None
    try:
        offset = int(cmds.promptDialog(query=True, text=True).strip())
    except ValueError:
        raise ValueError("Offset must be an integer.")
    if offset < 0 or offset > count:
        raise ValueError("Offset must be between 0 and the object count.")
    objects = nodes[2:2 + count]
    destinations = nodes[2 + count:2 + count * 2]
    fn = secondary.create_rope_roll if roll else secondary.create_rope_straight
    return fn(objects, nodes[0], nodes[1], destinations, nodes[-2], driver_attr, offset=offset)


def build_ui():
    cmds = _cmds()
    from aimayatool.ui.components import button_row, section

    section("Control shapes", spacing=False)
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, shape in (("Circle", "circle"), ("Box", "box"), ("Sphere", "sphere")):
        cmds.button(label=label, command=lambda *_, s=shape: _run("Created " + s, lambda: _create_selected(s)))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, shape in (("Diamond", "diamond"), ("Locator", "locator"), ("Eye", "eye")):
        cmds.button(label=label, command=lambda *_, s=shape: _run("Created " + s, lambda: _create_selected(s)))
    cmds.setParent("..")
    button_row([
        ("Replace Shape...", lambda *_: _run("Replaced shape", _replace_selected_shape)),
        ("Zero Group", lambda *_: _run("Zero group", _zero_selected)),
    ])

    section("Transforms and joints")
    button_row([
        ("Freeze TRS", lambda *_: __import__("aimayatool.ui.components", fromlist=["run_tracked_action"]).run_tracked_action("setup", "freeze_trs", "Freeze TRS", _freeze_selected)),
        ("Reset TR", lambda *_: _run("Reset", _reset_selected)),
        ("Create Joints", lambda *_: _run("Joints", _create_joints_selected))
    ])

    section("Constraints", "Selection order is explicit; driven object is selected last unless stated otherwise.")
    button_row([
        ("Parent Constraint", lambda *_: _run("Parent constraint", _parent_constraint_selected)),
        ("Point Constraint", lambda *_: _run("Point constraint", _point_constraint_selected))
    ])
    button_row([
        ("Orient Constraint", lambda *_: _run("Orient constraint", _orient_constraint_selected)),
        ("Aim Constraint", lambda *_: _run("Aim constraint", _aim_constraint_selected))
    ])

    section("Spaces and attributes")
    button_row([
        ("Create Space Switch", lambda *_: _run("Space switch", _space_switch_selected)),
        ("Copy Attribute...", lambda *_: _run("Attribute copy", _copy_attribute_selected))
    ])

    section("IK/FK", "RP IK: joints then controls. Blend: bind/FK/IK chains. Snap: alternating pairs. Switch: FK/IK nodes then proxies.")
    button_row([
        ("Create RP IK", lambda *_: _run("RP IK", _rp_ik_selected)),
        ("Create IK/FK Blend...", lambda *_: _run("IK/FK blend", _blend_ikfk_selected))
    ])
    button_row([
        ("Snap IK/FK...", lambda *_: _run("IK/FK snap", _snap_ikfk_selected)),
        ("Wire IK/FK Switch...", lambda *_: _run("IK/FK switch", _wire_ikfk_switch_selected))
    ])

    section("Secondary rigs", "Selection order is explicit; Fold/Rope prompts split ordered object/destination groups and driver configuration.")
    button_row([
        ("Spline IK Chain", lambda *_: _run("Spline IK", _spline_ik_selected)),
        ("Object on Curve", lambda *_: _run("Object on curve", _object_on_curve_selected)),
        ("Joints Between...", lambda *_: _run("Joints between", _joints_between_selected))
    ])
    button_row([
        ("Fold Rig...", lambda *_: _run("Fold rig", _fold_rig_selected)),
        ("Rope Straight...", lambda *_: _run("Rope straight", lambda: _rope_selected(False))),
        ("Rope Roll...", lambda *_: _run("Rope roll", lambda: _rope_selected(True)))
    ])

    cmds.separator(height=8, style="none")
    from . import naming_ui
    naming_ui.build_ui()
