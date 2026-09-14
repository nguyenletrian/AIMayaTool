from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _mesh_shape(cmds, node):
    if cmds.nodeType(node) == "mesh":
        return node
    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, type="mesh") or []
    if not shapes:
        raise ValueError("Mesh has no shape: {0}".format(node))
    return shapes[0]


def _copy_skin_to_plane(cmds, source_mesh, plane):
    history = cmds.listHistory(source_mesh, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster") or []
    if not skins:
        raise ValueError("Source mesh has no skinCluster: {0}".format(source_mesh))
    source_skin = skins[0]
    influences = cmds.skinCluster(source_skin, query=True, influence=True) or []
    if not influences:
        raise RuntimeError("Source skinCluster has no influences: {0}".format(source_skin))
    plane_skin = cmds.skinCluster(*(influences + [plane]), toSelectedBones=True, normalizeWeights=1, maximumInfluences=max(1, len(influences)), name=plane + "_Skin")[0]
    cmds.copySkinWeights(sourceSkin=source_skin, destinationSkin=plane_skin, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["name", "closestJoint"])
    return source_skin, plane_skin


def create_mesh_rivet(vertex_components, name, child=None, parent=None, copy_transform=None, bind_to_source=False):
    """Create the reusable surface-follow portion of the legacy ScenePattern Rivet.

    At least three vertex components from one mesh define a small polygon facet.
    A loft/pointOnSurfaceInfo network evaluates the facet center and orientation,
    driving a locator. Optionally a matched copy-transform group is parented below
    the locator, a child is driven through a zero group, and the facet can receive
    copied skin weights from the source mesh. UI/global state is intentionally absent.
    """
    cmds = _cmds(); vertices = [str(v) for v in (vertex_components or []) if v]
    if len(vertices) < 3:
        raise ValueError("Rivet requires at least three vertex components.")
    source_meshes = {v.split(".", 1)[0] for v in vertices if "." in v}
    if len(source_meshes) != 1:
        raise ValueError("Rivet vertices must belong to exactly one mesh.")
    source_mesh = next(iter(source_meshes)); _require_node(cmds, source_mesh, "Rivet source mesh")
    _mesh_shape(cmds, source_mesh)
    if child: _require_node(cmds, child, "Rivet child")
    if parent: _require_node(cmds, parent, "Rivet parent")
    if copy_transform: _require_node(cmds, copy_transform, "Rivet copy transform")
    if not name: raise ValueError("Rivet name is required.")

    positions = [cmds.pointPosition(vertex, world=True) for vertex in vertices]
    plane = cmds.polyCreateFacet(point=positions, name=name + "_Plane")[0]
    plane_shape = _mesh_shape(cmds, plane)
    edge_count = cmds.polyEvaluate(plane, edge=True)
    if edge_count < 3:
        raise RuntimeError("Rivet facet requires at least three edges.")

    curve_a = cmds.createNode("curveFromMeshEdge", name=name + "_EdgeCurveA")
    curve_b = cmds.createNode("curveFromMeshEdge", name=name + "_EdgeCurveB")
    loft = cmds.createNode("loft", name=name + "_Loft")
    posi = cmds.createNode("pointOnSurfaceInfo", name=name + "_POSI")
    cmds.setAttr(curve_a + ".edgeIndex[0]", 0); cmds.setAttr(curve_b + ".edgeIndex[0]", 2)
    cmds.setAttr(posi + ".turnOnPercentage", 1); cmds.setAttr(posi + ".parameterU", 0.5); cmds.setAttr(posi + ".parameterV", 0.5)
    cmds.connectAttr(plane_shape + ".worldMesh[0]", curve_a + ".inputMesh", force=True)
    cmds.connectAttr(plane_shape + ".worldMesh[0]", curve_b + ".inputMesh", force=True)
    cmds.connectAttr(curve_a + ".outputCurve", loft + ".inputCurve[0]", force=True)
    cmds.connectAttr(curve_b + ".outputCurve", loft + ".inputCurve[1]", force=True)
    cmds.connectAttr(loft + ".outputSurface", posi + ".inputSurface", force=True)

    locator = cmds.spaceLocator(name=name + "_Loc")[0]
    aim = cmds.createNode("aimConstraint", name=name + "_AimConstraint", parent=locator)
    cmds.setAttr(aim + ".aimVector", 0, 1, 0, type="double3"); cmds.setAttr(aim + ".upVector", 0, 0, 1, type="double3")
    cmds.connectAttr(posi + ".position", locator + ".translate", force=True)
    cmds.connectAttr(posi + ".normal", aim + ".target[0].targetTranslate", force=True)
    cmds.connectAttr(posi + ".tangentV", aim + ".worldUpVector", force=True)
    cmds.connectAttr(aim + ".constraintRotateX", locator + ".rotateX", force=True)
    cmds.connectAttr(aim + ".constraintRotateY", locator + ".rotateY", force=True)
    cmds.connectAttr(aim + ".constraintRotateZ", locator + ".rotateZ", force=True)

    copy_group = None
    if copy_transform:
        copy_group = cmds.group(empty=True, name=name + "_CopyTransform")
        matrix = cmds.xform(copy_transform, query=True, worldSpace=True, matrix=True)
        cmds.xform(copy_group, worldSpace=True, matrix=matrix); cmds.parent(copy_group, locator)

    child_offset = child_constraint = None
    if child:
        child_offset = cmds.group(empty=True, name=child + "_RivetOffset")
        matrix = cmds.xform(child, query=True, worldSpace=True, matrix=True)
        cmds.xform(child_offset, worldSpace=True, matrix=matrix)
        old_parent = (cmds.listRelatives(child, parent=True, fullPath=False) or [None])[0]
        if old_parent: cmds.parent(child_offset, old_parent)
        cmds.parent(child, child_offset)
        child_constraint = cmds.parentConstraint(locator, child_offset, maintainOffset=True)[0]

    source_skin = plane_skin = None
    if bind_to_source:
        source_skin, plane_skin = _copy_skin_to_plane(cmds, source_mesh, plane)
    if parent:
        cmds.parent(plane, parent); cmds.parent(locator, parent)

    return {"source_mesh": source_mesh, "vertices": tuple(vertices), "plane": plane, "plane_shape": plane_shape, "locator": locator, "aim_constraint": aim, "curve_nodes": (curve_a, curve_b), "loft": loft, "point_on_surface": posi, "copy_group": copy_group, "child_offset": child_offset, "child_constraint": child_constraint, "source_skin": source_skin, "plane_skin": plane_skin}
