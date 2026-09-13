from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def skin_cluster(node):
    cluster = skin.find_skin_cluster(node)
    if not cluster:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return cluster


def value(node):
    cluster = skin_cluster(node)
    return float(cmds.getAttr(cluster + '.envelope'))


def set_value(node, envelope):
    cluster = skin_cluster(node)
    envelope = float(envelope)
    cmds.setAttr(cluster + '.envelope', envelope)
    return float(cmds.getAttr(cluster + '.envelope'))


def enable(node):
    return set_value(node, 1.0)


def disable(node):
    return set_value(node, 0.0)


def toggle(node):
    return set_value(node, 0.0 if value(node) > 0.0 else 1.0)


def snapshot(nodes):
    result = {}
    for node in nodes or []:
        cluster = skin_cluster(node)
        result[cluster] = float(cmds.getAttr(cluster + '.envelope'))
    return result


def restore(snapshot):
    restored = {}
    for cluster, envelope in (snapshot or {}).items():
        plug = cluster + '.envelope'
        if cmds.objExists(plug):
            cmds.setAttr(plug, float(envelope))
            restored[cluster] = float(cmds.getAttr(plug))
    return restored
