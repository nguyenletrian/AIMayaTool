"""Bounded Maya smoke validation for the CreateRef transform primitive."""
from __future__ import absolute_import


def run():
    import maya.cmds as cmds
    from .transforms import create_reference_transform, world_matrix

    def delta(a, b):
        return max(abs(float(x) - float(y)) for x, y in zip(a, b))

    source = cmds.createNode("transform", name="AIBridgeCreateRefSource")
    cmds.setAttr(source + ".translate", 3.25, -1.5, 7.0, type="double3")
    cmds.setAttr(source + ".rotate", 17.0, -28.0, 43.0, type="double3")
    cmds.setAttr(source + ".scale", 1.2, 0.8, 1.35, type="double3")
    source_matrix = world_matrix(source)

    ref = create_reference_transform(source)
    default_name = ref.rsplit("|", 1)[-1]
    if default_name != "AIBridgeCreateRefSource_Ref":
        raise AssertionError("Unexpected default CreateRef name: {0}".format(default_name))
    if cmds.listRelatives(ref, shapes=True) or cmds.listRelatives(ref, children=True):
        raise AssertionError("CreateRef default result must be an empty transform")
    default_delta = delta(source_matrix, world_matrix(ref))
    if default_delta > 1e-8:
        raise AssertionError("CreateRef default world-matrix delta too large: {0}".format(default_delta))

    parent = cmds.createNode("transform", name="AIBridgeCreateRefParent")
    cmds.setAttr(parent + ".translate", -5.0, 2.0, 4.0, type="double3")
    cmds.setAttr(parent + ".rotate", -11.0, 31.0, 9.0, type="double3")
    parented = create_reference_transform(source, name="AIBridgeCreateRefExplicit", parent=parent)
    parented_delta = delta(source_matrix, world_matrix(parented))
    parent_rel = cmds.listRelatives(parented, parent=True) or []
    if not parent_rel or parent_rel[0] != parent:
        raise AssertionError("CreateRef explicit parent relationship was not preserved")
    if parented_delta > 1e-8:
        raise AssertionError("CreateRef parented world-matrix delta too large: {0}".format(parented_delta))

    missing_source = False
    try:
        create_reference_transform("AIBridgeMissingCreateRefSource")
    except ValueError:
        missing_source = True
    if not missing_source:
        raise AssertionError("Missing CreateRef source did not raise ValueError")

    missing_parent = False
    try:
        create_reference_transform(source, parent="AIBridgeMissingCreateRefParent")
    except ValueError:
        missing_parent = True
    if not missing_parent:
        raise AssertionError("Missing CreateRef parent did not raise ValueError")

    return "CREATE_REF_OK default={0} explicit={1} parent={2} default_delta={3:.3g} parented_delta={4:.3g} missing_source={5} missing_parent={6}".format(
        default_name,
        parented.rsplit("|", 1)[-1],
        parent,
        default_delta,
        parented_delta,
        missing_source,
        missing_parent,
    )
