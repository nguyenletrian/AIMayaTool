from __future__ import absolute_import

from aimayatool.tools.setup import controls


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _short_name(node):
    return str(node).split("|")[-1]


def _global_offset(cmds, child, suffix="_GlobalGrp"):
    expected = _short_name(child) + suffix
    parents = cmds.listRelatives(child, parent=True, fullPath=True) or []
    if parents and _short_name(parents[0]) == expected:
        offset = parents[0]
        root_parents = cmds.listRelatives(offset, parent=True, fullPath=True) or []
        if not root_parents:
            raise ValueError("Global offset has no root parent: {0}".format(offset))
        return offset, root_parents[0], False
    if not parents:
        raise ValueError("Global pattern child has no parent: {0}".format(child))
    root_parent = parents[0]
    offset, child_path = controls.create_zero_group(child, suffix=suffix)
    return offset, root_parent, True


def _disconnect_rotation_inputs(cmds, node):
    for attr in ("rx", "ry", "rz"):
        plug = "{0}.{1}".format(node, attr)
        for source in cmds.listConnections(plug, source=True, destination=False, plugs=True) or []:
            cmds.disconnectAttr(source, plug)


def _ensure_blend_attribute(cmds, child, attr_name, default_value):
    plug = "{0}.{1}".format(child, attr_name)
    if not cmds.objExists(plug):
        cmds.addAttr(
            child,
            longName=attr_name,
            attributeType="double",
            min=0.0,
            max=1.0,
            defaultValue=float(default_value),
        )
        cmds.setAttr(plug, edit=True, keyable=True)
    return plug


def execute_global_pattern_plan(plan):
    """Execute host-independent Global ScenePattern operations in Maya."""
    cmds = _cmds()
    results = []
    for operation in tuple(plan or ()):
        if operation.get("operation") != "global_parent_blend":
            raise ValueError("Unsupported Global ScenePattern operation: {0}".format(operation.get("operation")))
        child = operation.get("child")
        if not child or not cmds.objExists(child):
            results.append({"child": child, "status": "skipped_missing_child"})
            continue

        parent = operation.get("parent")
        _require_node(cmds, parent, "Global parent")
        attr_name = str(operation.get("attr_name") or "").strip()
        if not attr_name:
            raise ValueError("Global blend attribute name must be non-empty.")
        maintain_offset = bool(operation.get("maintain_offset", True))
        default_value = float(operation.get("default_value", 0.0))
        attr_plug = _ensure_blend_attribute(cmds, child, attr_name, default_value)
        offset, root_parent, created_offset = _global_offset(cmds, child)

        blend = cmds.shadingNode("blendColors", asUtility=True)
        parent_constraint = cmds.parentConstraint(root_parent, offset, mo=maintain_offset)[0]
        cmds.setAttr(parent_constraint + ".interpType", 2)
        _disconnect_rotation_inputs(cmds, offset)

        orient_constraint = cmds.orientConstraint(parent, offset, mo=maintain_offset)[0]
        _disconnect_rotation_inputs(cmds, offset)

        cmds.connectAttr(parent_constraint + ".constraintRotate", blend + ".color2", force=True)
        cmds.connectAttr(orient_constraint + ".constraintRotate", blend + ".color1", force=True)
        cmds.connectAttr(blend + ".output", offset + ".rotate", force=True)
        cmds.connectAttr(attr_plug, blend + ".blender", force=True)

        results.append({
            "child": child,
            "status": "applied",
            "offset": offset,
            "root_parent": root_parent,
            "created_offset": created_offset,
            "attribute": attr_plug,
            "blend": blend,
            "parent_constraint": parent_constraint,
            "orient_constraint": orient_constraint,
        })
    return tuple(results)
