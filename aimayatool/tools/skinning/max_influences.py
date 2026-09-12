from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def _skin_and_mesh(node):
    data = skin.skin_data(node)
    if not data['skin_cluster']:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return data['skin_cluster'], data['mesh']


def configured_limit(skin_cluster):
    if not skin_cluster or not cmds.objExists(skin_cluster):
        raise RuntimeError('Invalid skinCluster: %s' % skin_cluster)
    return int(cmds.getAttr(skin_cluster + '.maxInfluences'))


def _resolved_limit(skin_cluster, max_influences):
    limit = configured_limit(skin_cluster) if max_influences is None else int(max_influences)
    if limit < 1:
        raise ValueError('max_influences must be >= 1')
    return limit


def _vertex_weights(skin_cluster, vertex):
    joints = skin.influences(skin_cluster)
    values = cmds.skinPercent(skin_cluster, vertex, query=True, value=True) or []
    return list(zip(joints, values))


def _vertices(mesh):
    count = int(cmds.polyEvaluate(mesh, vertex=True) or 0)
    return ['%s.vtx[%d]' % (mesh, index) for index in range(count)]


def violating_vertices(node, max_influences=None, epsilon=1e-8):
    skin_cluster, mesh = _skin_and_mesh(node)
    limit = _resolved_limit(skin_cluster, max_influences)
    violating = []
    for vertex in _vertices(mesh):
        count = sum(1 for _, value in _vertex_weights(skin_cluster, vertex) if abs(value) > epsilon)
        if count > limit:
            violating.append(vertex)
    return violating


def fix(node, max_influences=None, epsilon=1e-8):
    skin_cluster, _ = _skin_and_mesh(node)
    limit = _resolved_limit(skin_cluster, max_influences)
    violating = violating_vertices(node, max_influences=limit, epsilon=epsilon)
    fixed = []
    for vertex in violating:
        weighted = [(joint, value) for joint, value in _vertex_weights(skin_cluster, vertex) if abs(value) > epsilon]
        weighted.sort(key=lambda item: item[1], reverse=True)
        zero_pairs = [(joint, 0.0) for joint, _ in weighted[limit:]]
        if zero_pairs:
            cmds.skinPercent(skin_cluster, vertex, transformValue=zero_pairs, normalize=True)
        fixed.append(vertex)
    return fixed


def _selected_target():
    items = cmds.ls(selection=True, flatten=True) or []
    if not items:
        raise RuntimeError('Select a skinned mesh or component.')
    return items[0]


def check_from_selection(max_influences=None):
    return violating_vertices(_selected_target(), max_influences=max_influences)


def fix_from_selection(max_influences=None):
    return fix(_selected_target(), max_influences=max_influences)
