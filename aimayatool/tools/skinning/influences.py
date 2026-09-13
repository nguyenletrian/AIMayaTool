from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def context_from_selection(selection=None):
    items = list(selection) if selection is not None else (cmds.ls(selection=True, flatten=True) or [])
    joints = [item for item in items if cmds.nodeType(item.split('.', 1)[0]) == 'joint']
    targets = [item for item in items if item not in joints]
    if not targets:
        raise RuntimeError('Select a skinned mesh/component and one or more joints.')
    data = skin.skin_data(targets[0])
    if not data['skin_cluster']:
        raise RuntimeError('Selected mesh/component has no skinCluster.')
    if not joints:
        raise RuntimeError('Select one or more joints with the skinned mesh/component.')
    return data, joints


def add(node, joints, weight=0.0, lock_weights=True):
    data = skin.skin_data(node)
    if not data['skin_cluster']:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return skin.add_influences(data['skin_cluster'], joints, weight=weight, lock_weights=lock_weights)


def remove(node, joints):
    data = skin.skin_data(node)
    if not data['skin_cluster']:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return skin.remove_influences(data['skin_cluster'], joints)


def add_missing_from_source(source, targets, weight=0.0, lock_weights=False):
    source_data = skin.skin_data(source)
    if not source_data['skin_cluster']:
        raise RuntimeError('Source has no skinCluster: %s' % source)
    source_influences = source_data['influences'] or []
    report = {}
    for target in targets or []:
        target_data = skin.skin_data(target)
        if not target_data['skin_cluster']:
            raise RuntimeError('Target has no skinCluster: %s' % target)
        added = skin.add_influences(
            target_data['skin_cluster'],
            source_influences,
            weight=weight,
            lock_weights=lock_weights,
        )
        report[target] = added
    return report


def remove_unused(node):
    data = skin.skin_data(node)
    skin_cluster = data['skin_cluster']
    if not skin_cluster:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    before = list(data['influences'] or [])
    if len(before) <= 1:
        return []
    cmds.skinCluster(skin_cluster, edit=True, removeUnusedInfluence=True)
    after = set(skin.influences(skin_cluster))
    return [joint for joint in before if joint not in after]


def add_from_selection():
    data, joints = context_from_selection()
    return skin.add_influences(data['skin_cluster'], joints)


def remove_from_selection():
    data, joints = context_from_selection()
    return skin.remove_influences(data['skin_cluster'], joints)


def add_missing_from_selection():
    items = cmds.ls(selection=True, objectsOnly=True, long=True) or []
    if len(items) < 2:
        raise RuntimeError('Select source skinned mesh first, then target skinned mesh(es).')
    return add_missing_from_source(items[0], items[1:])


def remove_unused_from_selection():
    items = cmds.ls(selection=True, objectsOnly=True, long=True) or []
    if not items:
        raise RuntimeError('Select one or more skinned meshes.')
    return {item: remove_unused(item) for item in items}
