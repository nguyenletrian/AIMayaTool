from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def create_plane_projection(reference_nodes, control, projected=None, name_prefix="planeProjection"):
    """Project a control position onto the live plane defined by three references.

    The legacy PointOnPlane network is preserved as a composable primitive: three world
    positions define the plane, the control supplies the point to project, and the result
    drives an explicit projected transform. The final world-space point is localized
    through projected.parentInverseMatrix so parented outputs remain correct.
    """
    cmds = _cmds(); references = list(reference_nodes or [])
    if len(references) != 3:
        raise ValueError("Plane projection requires exactly three reference nodes.")
    for node in references:
        _require_node(cmds, node, "Plane reference")
    _require_node(cmds, control, "Projection control")
    prefix = name_prefix or "planeProjection"
    if projected is None:
        projected = cmds.createNode("transform", name=prefix + "_Projected")
    else:
        _require_node(cmds, projected, "Projected transform")

    decomps = []
    for index, node in enumerate(references, start=1):
        decomp = cmds.createNode("decomposeMatrix", name="{0}_Ref{1:02d}World".format(prefix, index))
        cmds.connectAttr(node + ".worldMatrix[0]", decomp + ".inputMatrix", force=True)
        decomps.append(decomp)
    control_decomp = cmds.createNode("decomposeMatrix", name=prefix + "_ControlWorld")
    cmds.connectAttr(control + ".worldMatrix[0]", control_decomp + ".inputMatrix", force=True)

    vector_a = cmds.createNode("plusMinusAverage", name=prefix + "_PlaneVectorA")
    vector_b = cmds.createNode("plusMinusAverage", name=prefix + "_PlaneVectorB")
    for node in (vector_a, vector_b): cmds.setAttr(node + ".operation", 2)
    cmds.connectAttr(decomps[1] + ".outputTranslate", vector_a + ".input3D[0]", force=True)
    cmds.connectAttr(decomps[0] + ".outputTranslate", vector_a + ".input3D[1]", force=True)
    cmds.connectAttr(decomps[2] + ".outputTranslate", vector_b + ".input3D[0]", force=True)
    cmds.connectAttr(decomps[0] + ".outputTranslate", vector_b + ".input3D[1]", force=True)

    normal = cmds.createNode("vectorProduct", name=prefix + "_PlaneNormal")
    cmds.setAttr(normal + ".operation", 2); cmds.setAttr(normal + ".normalizeOutput", 1)
    cmds.connectAttr(vector_a + ".output3D", normal + ".input1", force=True)
    cmds.connectAttr(vector_b + ".output3D", normal + ".input2", force=True)

    control_vector = cmds.createNode("plusMinusAverage", name=prefix + "_ControlFromPlane")
    cmds.setAttr(control_vector + ".operation", 2)
    cmds.connectAttr(control_decomp + ".outputTranslate", control_vector + ".input3D[0]", force=True)
    cmds.connectAttr(decomps[0] + ".outputTranslate", control_vector + ".input3D[1]", force=True)

    dot = cmds.createNode("vectorProduct", name=prefix + "_PlaneDistance")
    cmds.setAttr(dot + ".operation", 1)
    cmds.connectAttr(control_vector + ".output3D", dot + ".input1", force=True)
    cmds.connectAttr(normal + ".output", dot + ".input2", force=True)

    offset = cmds.createNode("multiplyDivide", name=prefix + "_NormalOffset")
    cmds.setAttr(offset + ".operation", 1)
    cmds.connectAttr(normal + ".output", offset + ".input1", force=True)
    for axis in "XYZ": cmds.connectAttr(dot + ".outputX", offset + ".input2" + axis, force=True)

    projected_world = cmds.createNode("plusMinusAverage", name=prefix + "_ProjectedWorld")
    cmds.setAttr(projected_world + ".operation", 2)
    cmds.connectAttr(control_decomp + ".outputTranslate", projected_world + ".input3D[0]", force=True)
    cmds.connectAttr(offset + ".output", projected_world + ".input3D[1]", force=True)

    localize = cmds.createNode("pointMatrixMult", name=prefix + "_ProjectedLocal")
    cmds.connectAttr(projected_world + ".output3D", localize + ".inPoint", force=True)
    cmds.connectAttr(projected + ".parentInverseMatrix[0]", localize + ".inMatrix", force=True)
    cmds.connectAttr(localize + ".output", projected + ".translate", force=True)
    utility_nodes = tuple(decomps + [control_decomp, vector_a, vector_b, normal, control_vector, dot, offset, projected_world, localize])
    return {"references": tuple(references), "control": control, "projected": projected, "utility_nodes": utility_nodes, "normal_node": normal, "projected_world_node": projected_world, "localize_node": localize}
