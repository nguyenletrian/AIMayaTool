from __future__ import absolute_import

import maya.cmds as cmds


def mesh_from_component(node):
    return (node or "").split(".", 1)[0]


def find_skin_cluster(node):
    mesh = mesh_from_component(node)
    if not mesh or not cmds.objExists(mesh):
        return None
    shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True, fullPath=True) or []
    search_node = shapes[0] if shapes else mesh
    history = cmds.listHistory(search_node, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster") or []
    return skins[0] if skins else None


def influences(skin_cluster):
    if not skin_cluster or not cmds.objExists(skin_cluster):
        return []
    return cmds.skinCluster(skin_cluster, query=True, influence=True) or []


def skin_data(node):
    mesh = mesh_from_component(node)
    skin_cluster = find_skin_cluster(mesh)
    return {
        "mesh": mesh if skin_cluster else None,
        "skin_cluster": skin_cluster,
        "influences": influences(skin_cluster),
    }


def add_influences(skin_cluster, joints, weight=0.0, lock_weights=True):
    current = set(influences(skin_cluster))
    added = []
    for joint in joints or []:
        if joint in current or not cmds.objExists(joint):
            continue
        cmds.skinCluster(
            skin_cluster,
            edit=True,
            addInfluence=joint,
            weight=weight,
            lockWeights=lock_weights,
        )
        current.add(joint)
        added.append(joint)
    return added


def remove_influences(skin_cluster, joints):
    current = set(influences(skin_cluster))
    removed = []
    for joint in joints or []:
        if joint not in current:
            continue
        cmds.skinCluster(skin_cluster, edit=True, removeInfluence=joint)
        current.discard(joint)
        removed.append(joint)
    return removed
