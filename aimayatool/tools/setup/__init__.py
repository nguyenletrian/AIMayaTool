from __future__ import absolute_import

import traceback

from .controls import create_controls_for_nodes, create_zero_group, replace_control_shape, available_shapes


def _cmds():
    import maya.cmds as cmds
    return cmds


def _selected_transforms():
    cmds = _cmds()
    return cmds.ls(selection=True, long=True, type="transform") or []


def _run(label, fn):
    cmds = _cmds()
    try:
        result = fn()
        text = str(result) if result else "no changes"
        cmds.inViewMessage(amg="{0}: {1}".format(label, text), pos="midCenter", fade=True)
        return result
    except Exception as exc:
        message = "{0} failed: {1}".format(label, exc)
        cmds.warning("AIMayaTool Setup: " + message)
        try:
            cmds.inViewMessage(amg="<hl>{0}</hl>".format(message), pos="midCenter", fade=True)
        except Exception:
            pass
        traceback.print_exc()
        return None


def _require_selection(minimum, usage):
    nodes = _selected_transforms()
    if len(nodes) < minimum:
        raise ValueError(usage)
    return nodes


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


def build_ui():
    cmds = _cmds()

    cmds.text(label="Control shapes", align="left")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, shape in (("Circle", "circle"), ("Box", "box"), ("Sphere", "sphere")):
        cmds.button(label=label, command=lambda *_, s=shape: _run("Created " + s, lambda: _create_selected(s)))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, shape in (("Diamond", "diamond"), ("Locator", "locator"), ("Eye", "eye")):
        cmds.button(label=label, command=lambda *_, s=shape: _run("Created " + s, lambda: _create_selected(s)))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Replace Shape...", command=lambda *_: _run("Replaced shape", _replace_selected_shape))
    cmds.button(label="Zero Group", command=lambda *_: _run("Zero group", _zero_selected))
    cmds.setParent("..")

    cmds.separator(height=8, style="none")
    cmds.text(label="Transforms and joints", align="left")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    cmds.button(label="Freeze TRS", command=lambda *_: _run("Freeze", _freeze_selected))
    cmds.button(label="Reset TR", command=lambda *_: _run("Reset", _reset_selected))
    cmds.button(label="Create Joints", command=lambda *_: _run("Joints", _create_joints_selected))
    cmds.setParent("..")

    cmds.separator(height=8, style="none")
    cmds.text(label="Constraints", align="left")
    cmds.text(label="Selection order is explicit; driven object is selected last unless stated otherwise.", align="left")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Parent Constraint", command=lambda *_: _run("Parent constraint", _parent_constraint_selected))
    cmds.button(label="Point Constraint", command=lambda *_: _run("Point constraint", _point_constraint_selected))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Orient Constraint", command=lambda *_: _run("Orient constraint", _orient_constraint_selected))
    cmds.button(label="Aim Constraint", command=lambda *_: _run("Aim constraint", _aim_constraint_selected))
    cmds.setParent("..")

    cmds.separator(height=8, style="none")
    cmds.text(label="Spaces and attributes", align="left")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Create Space Switch", command=lambda *_: _run("Space switch", _space_switch_selected))
    cmds.button(label="Copy Attribute...", command=lambda *_: _run("Attribute copy", _copy_attribute_selected))
    cmds.setParent("..")
