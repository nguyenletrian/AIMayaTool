from __future__ import absolute_import

import time

import maya.cmds as cmds

from .undo import undo_chunk


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


def skin_data_many(nodes):
    """Resolve skin data once per mesh while preserving input order and result shape."""
    cache = {}
    result = []
    for node in nodes or []:
        mesh = mesh_from_component(node)
        if mesh not in cache:
            cache[mesh] = skin_data(mesh)
        result.append(dict(cache[mesh]))
    return result


def add_influences(skin_cluster, joints, weight=0.0, lock_weights=True):
    current = set(influences(skin_cluster))
    added = []
    with undo_chunk('AIMayaTool Add Skin Influences'):
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
    with undo_chunk('AIMayaTool Remove Skin Influences'):
        for joint in joints or []:
            if joint not in current:
                continue
            cmds.skinCluster(skin_cluster, edit=True, removeInfluence=joint)
            current.discard(joint)
            removed.append(joint)
    return removed


def undo_safety_baseline_managed_maya_smoke():
    """Measure current multi-influence mutation undo behavior before hardening."""
    mesh = cmds.polyPlane(name='AIBridgeUndoSkinBaseline', subdivisionsX=1, subdivisionsY=1)[0]
    root = cmds.joint(name='AIBridgeUndoSkinRoot')
    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIBridgeUndoSkinA')
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIBridgeUndoSkinB')
    skin_cluster = cmds.skinCluster(root, mesh, toSelectedBones=True, name='AIBridgeUndoSkinCluster')[0]
    before_selection = cmds.ls(selection=True, long=True) or []
    cmds.flushUndo()
    added = add_influences(skin_cluster, [joint_a, joint_b])
    after_add = set(influences(skin_cluster))
    cmds.undo()
    after_one_undo = set(influences(skin_cluster))
    second_undo_available = True
    try:
        cmds.undo()
    except RuntimeError as exc:
        if 'no more commands to undo' not in str(exc).lower():
            raise
        second_undo_available = False
    after_two_undos = set(influences(skin_cluster))
    selection_preserved = (cmds.ls(selection=True, long=True) or []) == before_selection
    expected_added = set([joint_a, joint_b]).issubset(after_add)
    one_step_complete = joint_a not in after_one_undo and joint_b not in after_one_undo
    two_steps_complete = joint_a not in after_two_undos and joint_b not in after_two_undos
    return {'operation': 'skin_add_influences_undo_baseline', 'added_count': len(added), 'expected_added': expected_added, 'one_step_complete': one_step_complete, 'two_steps_complete': two_steps_complete, 'second_undo_available': second_undo_available, 'selection_preserved': selection_preserved}


def undo_safety_remove_managed_maya_smoke():
    """Validate that removing multiple skin influences is one Maya undo step."""
    mesh = cmds.polyPlane(name='AIBridgeUndoSkinRemove', subdivisionsX=1, subdivisionsY=1)[0]
    root = cmds.joint(name='AIBridgeUndoSkinRemoveRoot')
    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIBridgeUndoSkinRemoveA')
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIBridgeUndoSkinRemoveB')
    skin_cluster = cmds.skinCluster(root, mesh, toSelectedBones=True, name='AIBridgeUndoSkinRemoveCluster')[0]
    add_influences(skin_cluster, [joint_a, joint_b])
    before_selection = cmds.ls(selection=True, long=True) or []
    cmds.flushUndo()
    removed = remove_influences(skin_cluster, [joint_a, joint_b])
    after_remove = set(influences(skin_cluster))
    cmds.undo()
    after_one_undo = set(influences(skin_cluster))
    selection_preserved = (cmds.ls(selection=True, long=True) or []) == before_selection
    expected_removed = joint_a not in after_remove and joint_b not in after_remove
    one_step_restored = joint_a in after_one_undo and joint_b in after_one_undo
    return {'operation': 'skin_remove_influences_undo', 'removed_count': len(removed), 'expected_removed': expected_removed, 'one_step_restored': one_step_restored, 'selection_preserved': selection_preserved}


def performance_postchange_managed_maya_smoke():
    """Bounded managed-Maya baseline for repeated skin adapter discovery."""
    mesh = cmds.polyPlane(name='AIBridgeSkinBaseline', subdivisionsX=10, subdivisionsY=10)[0]
    joint = cmds.joint(name='AIBridgeSkinBaselineJoint')
    cmds.skinCluster(joint, mesh, toSelectedBones=True, name='AIBridgeSkinBaselineCluster')
    before = cmds.ls(selection=True, long=True) or []
    sample_count = 100
    start = time.perf_counter()
    results = skin_data_many([mesh] * sample_count)
    elapsed = time.perf_counter() - start
    valid = all(item.get('mesh') == mesh and item.get('skin_cluster') and joint in item.get('influences', []) for item in results)
    selection_preserved = (cmds.ls(selection=True, long=True) or []) == before
    if not valid or not selection_preserved:
        raise AssertionError('Skin adapter baseline changed result validity or selection state')
    return {'operation': 'skin_data_100_queries', 'sample_count': sample_count, 'elapsed_seconds': elapsed, 'valid_results': valid, 'selection_preserved': selection_preserved}


# Reusable benchmark entry point for the current implementation.
performance_baseline_managed_maya_smoke = performance_postchange_managed_maya_smoke
