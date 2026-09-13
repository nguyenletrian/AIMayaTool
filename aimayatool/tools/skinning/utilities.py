from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def _skin_cluster(node):
    skin_cluster = skin.find_skin_cluster(node)
    if not skin_cluster:
        raise RuntimeError('No skinCluster found: %s' % node)
    return skin_cluster


def _vertices(mesh):
    count = int(cmds.polyEvaluate(mesh, vertex=True) or 0)
    return ['%s.vtx[%d]' % (mesh, index) for index in range(count)]


def set_influence_lock(node, locked):
    skin_cluster = _skin_cluster(node)
    changed = []
    value = 1 if locked else 0
    for joint in skin.influences(skin_cluster):
        plug = joint + '.liw'
        if not cmds.objExists(plug):
            continue
        if int(cmds.getAttr(plug)) != value:
            cmds.setAttr(plug, value)
            changed.append(joint)
    return changed


def lock_all(node):
    return set_influence_lock(node, True)


def unlock_all(node):
    return set_influence_lock(node, False)


def prune(node, threshold=0.001, components=None):
    skin_cluster = _skin_cluster(node)
    targets = list(components or []) or [skin.mesh_from_component(node)]
    cmds.skinPercent(skin_cluster, targets, pruneWeights=float(threshold), normalize=True)
    return targets


def clear_influence(components, joint):
    component_list = list(components or [])
    if not component_list:
        raise RuntimeError('No vertices supplied.')
    mesh = skin.mesh_from_component(component_list[0])
    if any(skin.mesh_from_component(item) != mesh for item in component_list):
        raise RuntimeError('Vertices must belong to one mesh.')
    skin_cluster = _skin_cluster(mesh)
    influences = skin.influences(skin_cluster)
    if joint not in influences:
        raise RuntimeError('%s is not an influence of %s.' % (joint, skin_cluster))

    changed = []
    for vertex in component_list:
        weights = {name: float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=name) or 0.0) for name in influences}
        removed = weights.get(joint, 0.0)
        if removed <= 1e-12:
            continue
        remaining = [(name, value) for name, value in weights.items() if name != joint and value > 1e-12]
        if not remaining:
            raise RuntimeError('Cannot clear the only weighted influence on %s.' % vertex)
        total = sum(value for _, value in remaining)
        values = []
        for name in influences:
            if name == joint:
                values.append((name, 0.0))
            else:
                value = weights[name]
                values.append((name, value / total if total > 0.0 else 0.0))
        cmds.skinPercent(skin_cluster, vertex, transformValue=values, normalize=True)
        changed.append(vertex)
    return changed


def affected_vertices(node, joints, threshold=0.0001):
    mesh = skin.mesh_from_component(node)
    skin_cluster = _skin_cluster(mesh)
    valid = [joint for joint in joints or [] if joint in skin.influences(skin_cluster)]
    if not valid:
        return []
    result = []
    for vertex in _vertices(mesh):
        if any(float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=joint) or 0.0) > threshold for joint in valid):
            result.append(vertex)
    return result


def _selected_skin_node(items):
    for item in items:
        if cmds.nodeType(item.split('.', 1)[0]) == 'joint':
            continue
        mesh = skin.mesh_from_component(item)
        if skin.find_skin_cluster(mesh):
            return mesh
    return None


def lock_all_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    mesh = _selected_skin_node(items)
    if not mesh:
        raise RuntimeError('Select a skinned mesh or one of its vertices.')
    return lock_all(mesh)


def unlock_all_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    mesh = _selected_skin_node(items)
    if not mesh:
        raise RuntimeError('Select a skinned mesh or one of its vertices.')
    return unlock_all(mesh)


def prune_from_selection(threshold=0.001):
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    mesh = _selected_skin_node(items)
    if not mesh:
        raise RuntimeError('Select a skinned mesh or vertices.')
    components = [item for item in items if '.vtx[' in item and skin.mesh_from_component(item) == mesh]
    return prune(mesh, threshold=threshold, components=components)


def clear_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    joints = cmds.ls(items, type='joint', long=True) or []
    vertices = [item for item in items if '.vtx[' in item]
    if not joints or not vertices:
        raise RuntimeError('Select one influence joint and target vertices.')
    return clear_influence(vertices, joints[0])


def select_affected_from_selection(threshold=0.0001):
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    joints = cmds.ls(items, type='joint', long=True) or []
    mesh = _selected_skin_node(items)
    if not mesh or not joints:
        raise RuntimeError('Select a skinned mesh and one or more influence joints.')
    vertices = affected_vertices(mesh, joints, threshold=threshold)
    cmds.select(vertices, replace=True) if vertices else cmds.select(clear=True)
    return vertices
