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


def add_from_selection():
    data, joints = context_from_selection()
    return skin.add_influences(data['skin_cluster'], joints)


def remove_from_selection():
    data, joints = context_from_selection()
    return skin.remove_influences(data['skin_cluster'], joints)
