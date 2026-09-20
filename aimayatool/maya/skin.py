from __future__ import absolute_import

import time

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


def performance_baseline_managed_maya_smoke():
    """Bounded managed-Maya baseline for repeated skin adapter discovery."""
    mesh = cmds.polyPlane(name='AIBridgeSkinBaseline', subdivisionsX=10, subdivisionsY=10)[0]
    joint = cmds.joint(name='AIBridgeSkinBaselineJoint')
    cmds.skinCluster(joint, mesh, toSelectedBones=True, name='AIBridgeSkinBaselineCluster')
    before = cmds.ls(selection=True, long=True) or []
    sample_count = 100
    start = time.perf_counter()
    results = [skin_data(mesh) for _ in range(sample_count)]
    elapsed = time.perf_counter() - start
    valid = all(item.get('mesh') == mesh and item.get('skin_cluster') and joint in item.get('influences', []) for item in results)
    selection_preserved = (cmds.ls(selection=True, long=True) or []) == before
    if not valid or not selection_preserved:
        raise AssertionError('Skin adapter baseline changed result validity or selection state')
    return {'operation': 'skin_data_100_queries', 'sample_count': sample_count, 'elapsed_seconds': elapsed, 'valid_results': valid, 'selection_preserved': selection_preserved}
