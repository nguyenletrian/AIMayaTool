from __future__ import absolute_import

import re

_VERTEX_RE = re.compile(r"^(?P<mesh>.+)\.vtx\[(?P<index>\d+)\]$")


def _names(value):
    if isinstance(value, str):
        value = value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]


def normalize_rivet(data):
    data = data or {}
    vertices = _names(data.get("vertexs"))
    name = str(data.get("name", "")).strip()
    copy_transform = str(data.get("copyTransform", "")).strip()
    child = str(data.get("child", "")).strip()
    parent = str(data.get("parent", "")).strip()
    if len(vertices) < 3:
        raise ValueError("vertexs must contain at least three vertices")
    if not name:
        raise ValueError("name must not be empty")
    parsed = []
    for vertex in vertices:
        match = _VERTEX_RE.match(vertex)
        if not match:
            raise ValueError("Invalid mesh vertex component: " + vertex)
        parsed.append((match.group("mesh"), int(match.group("index"))))
    mesh = parsed[0][0]
    if any(item[0] != mesh for item in parsed):
        raise ValueError("All rivet vertices must belong to the same mesh")
    return {
        "vertexs": vertices,
        "mesh": mesh,
        "indices": [item[1] for item in parsed],
        "name": name,
        "copyTransform": copy_transform,
        "child": child,
        "parent": parent,
        "plane": name + "_Plane",
        "locator": name + "_Loc",
        "childOffset": child + "_RivetOffset" if child else "",
    }


def _shape(cmds, node, shape_type=None):
    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
    if shape_type:
        shapes = [shape for shape in shapes if cmds.nodeType(shape) == shape_type]
    if not shapes:
        raise ValueError("Missing%s shape: %s" % ((" " + shape_type) if shape_type else "", node))
    return shapes[0]


def _match_group(cmds, node, name):
    group = cmds.group(empty=True, name=name)
    cmds.matchTransform(group, node)
    return group


def _apply_rivet_unprotected(data):
    import maya.cmds as cmds

    plan = normalize_rivet(data)
    if not cmds.objExists(plan["mesh"]):
        raise ValueError("Missing source mesh: " + plan["mesh"])
    mesh_shape = _shape(cmds, plan["mesh"], "mesh")
    positions = [cmds.pointPosition(vertex, world=True) for vertex in plan["vertexs"]]
    plane = cmds.polyCreateFacet(point=positions, name=plan["plane"])[0]
    plane_shape = _shape(cmds, plane, "mesh")
    edges = cmds.ls(plane + ".e[*]", flatten=True) or []
    if len(edges) < 2:
        raise RuntimeError("Rivet plane requires at least two edges")
    curves = []
    for index, edge in enumerate(edges[:2]):
        cmds.select(edge, replace=True)
        curves.append(cmds.polyToCurve(form=2, degree=1, name=plan["name"] + "_EdgeCurve%d" % (index + 1))[0])
    surface = cmds.loft(curves[0], curves[1], constructionHistory=True, uniform=True, close=False, autoReverse=True, degree=1, sectionSpans=1, range=False, polygon=0, name=plan["name"] + "_Surface")[0]
    surface_shape = _shape(cmds, surface, "nurbsSurface")
    posi = cmds.createNode("pointOnSurfaceInfo", name=plan["name"] + "_POSI")
    cmds.connectAttr(surface_shape + ".worldSpace[0]", posi + ".inputSurface", force=True)
    cmds.setAttr(posi + ".parameterU", 0.5)
    cmds.setAttr(posi + ".parameterV", 0.5)
    locator = cmds.spaceLocator(name=plan["locator"])[0]
    cmds.connectAttr(posi + ".position", locator + ".translate", force=True)
    aim = cmds.createNode("aimConstraint", name=plan["name"] + "_AimConstraint", parent=locator)
    cmds.setAttr(aim + ".aimVector", 0, 1, 0, type="double3")
    cmds.setAttr(aim + ".upVector", 0, 0, 1, type="double3")
    cmds.connectAttr(posi + ".normal", aim + ".target[0].targetTranslate", force=True)
    cmds.connectAttr(posi + ".tangentV", aim + ".worldUpVector", force=True)
    cmds.connectAttr(aim + ".constraintRotate", locator + ".rotate", force=True)
    copied = ""
    if plan["copyTransform"]:
        if not cmds.objExists(plan["copyTransform"]):
            raise ValueError("Missing copyTransform: " + plan["copyTransform"])
        copied = _match_group(cmds, plan["copyTransform"], plan["name"] + "_CopyTransform")
        cmds.parent(copied, locator)
    child_offset = ""
    if plan["child"]:
        if not cmds.objExists(plan["child"]):
            raise ValueError("Missing child: " + plan["child"])
        child_offset = _match_group(cmds, plan["child"], plan["childOffset"])
        old_parent = (cmds.listRelatives(plan["child"], parent=True, fullPath=True) or [None])[0]
        if old_parent:
            cmds.parent(child_offset, old_parent)
        cmds.parent(plan["child"], child_offset)
        cmds.parentConstraint(locator, child_offset, maintainOffset=True)
    skin = cmds.ls(cmds.listHistory(mesh_shape) or [], type="skinCluster") or []
    if skin:
        influences = cmds.skinCluster(skin[0], query=True, influence=True) or []
        if influences:
            plane_skin = cmds.skinCluster(influences, plane, toSelectedBones=True)[0]
            cmds.copySkinWeights(sourceSkin=skin[0], destinationSkin=plane_skin, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=("name", "closestJoint"))
    if plan["parent"]:
        if not cmds.objExists(plan["parent"]):
            raise ValueError("Missing parent: " + plan["parent"])
        cmds.parent(plane, locator, plan["parent"])
    return {"plan": plan, "plane": plane, "locator": locator, "surface": surface, "curves": curves, "copyTransform": copied, "childOffset": child_offset}



def apply_rivet(data):
    import maya.cmds as cmds
    selection_uuids = cmds.ls(selection=True, uuid=True) or []
    try:
        return _apply_rivet_unprotected(data)
    finally:
        restored = []
        for node_uuid in selection_uuids:
            matches = cmds.ls(node_uuid, long=True) or []
            if matches:
                restored.append(matches[0])
        if restored:
            cmds.select(restored, replace=True)
        else:
            cmds.select(clear=True)

def rivet_managed_maya_smoke():
    import maya.cmds as cmds

    mesh = cmds.polyPlane(name="AIBridgeRivetSource", subdivisionsX=1, subdivisionsY=1)[0]
    child = cmds.createNode("transform", name="AIBridgeRivetChild")
    result = apply_rivet({"vertexs": "\n".join([mesh + ".vtx[0]", mesh + ".vtx[1]", mesh + ".vtx[2]"]), "name": "AIBridgeRivet", "child": child})
    checks = {"plane": cmds.objExists(result["plane"]), "locator": cmds.objExists(result["locator"]), "surface": cmds.objExists(result["surface"]), "child_offset": cmds.objExists(result["childOffset"])}
    if not all(checks.values()):
        raise RuntimeError("Rivet smoke failed: {0}".format(checks))
    return {"ok": True, "checks": checks}

def rivet_selection_state_managed_maya_smoke():
    """Measure whether Rivet construction preserves an unrelated explicit selection."""
    import maya.cmds as cmds

    mesh = cmds.polyPlane(name="AIBridgeRivetStateSource", subdivisionsX=1, subdivisionsY=1)[0]
    child = cmds.createNode("transform", name="AIBridgeRivetStateChild")
    sentinel = cmds.createNode("transform", name="AIBridgeRivetStateSentinel")
    cmds.select(sentinel, replace=True)
    before = cmds.ls(selection=True, long=True) or []
    result = apply_rivet({
        "vertexs": "\n".join([mesh + ".vtx[0]", mesh + ".vtx[1]", mesh + ".vtx[2]"]),
        "name": "AIBridgeRivetState",
        "child": child,
    })
    after = cmds.ls(selection=True, long=True) or []
    functional = bool(
        cmds.objExists(result["plane"])
        and cmds.objExists(result["locator"])
        and cmds.objExists(result["surface"])
        and cmds.objExists(result["childOffset"])
    )
    return {
        "operation": "rivet_selection_state",
        "functional": functional,
        "selection_preserved": before == after,
        "before": before,
        "after": after,
    }

