from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import paint_state


def _skin_cluster(node):
    skin_cluster = skin.find_skin_cluster(node)
    if not skin_cluster:
        raise RuntimeError('Target has no skinCluster: %s' % node)
    return skin_cluster


def lock_state(node):
    skin_cluster = _skin_cluster(node)
    return {
        influence: bool(cmds.getAttr(influence + '.liw'))
        for influence in skin.influences(skin_cluster)
        if cmds.objExists(influence + '.liw')
    }


def set_locked(influence, locked=True):
    if not cmds.objExists(influence + '.liw'):
        raise RuntimeError('Influence does not expose lockInfluenceWeights: %s' % influence)
    cmds.setAttr(influence + '.liw', bool(locked))
    return bool(cmds.getAttr(influence + '.liw'))


def set_all_locked(node, locked=True):
    skin_cluster = _skin_cluster(node)
    result = {}
    for influence in skin.influences(skin_cluster):
        if cmds.objExists(influence + '.liw'):
            result[influence] = set_locked(influence, locked)
    return result


def isolate(node, active_influence):
    skin_cluster = _skin_cluster(node)
    influences = skin.influences(skin_cluster)
    if active_influence not in influences:
        raise ValueError('Influence is not bound to target: %s' % active_influence)
    previous = lock_state(node)
    for influence in influences:
        if cmds.objExists(influence + '.liw'):
            set_locked(influence, influence != active_influence)
    return previous


def restore(snapshot):
    restored = {}
    for influence, locked in (snapshot or {}).items():
        if cmds.objExists(influence + '.liw'):
            restored[influence] = set_locked(influence, locked)
    return restored


def unlock_only(node, influences):
    skin_cluster = _skin_cluster(node)
    bound = skin.influences(skin_cluster)
    requested = [influence for influence in influences or [] if influence in bound]
    if not requested:
        raise ValueError('No requested influences are bound to target: %s' % node)
    result = {}
    requested_set = set(requested)
    for influence in bound:
        if cmds.objExists(influence + '.liw'):
            result[influence] = set_locked(influence, influence not in requested_set)
    return requested


def top_two_influences(vertex):
    mesh = skin.mesh_from_component(vertex)
    skin_cluster = _skin_cluster(mesh)
    weighted = []
    for influence in skin.influences(skin_cluster):
        weight = float(cmds.skinPercent(skin_cluster, vertex, query=True, transform=influence) or 0.0)
        if weight > 0.0:
            weighted.append((weight, influence))
    weighted.sort(key=lambda item: item[0], reverse=True)
    if len(weighted) < 2:
        raise RuntimeError('Vertex has fewer than two weighted influences: %s' % vertex)
    return [weighted[0][1], weighted[1][1]]


def unlock_top_two(vertex):
    influences = top_two_influences(vertex)
    unlock_only(skin.mesh_from_component(vertex), influences)
    return influences


def relative_influence(node, influence, direction):
    bound = skin.influences(_skin_cluster(node))
    if influence not in bound:
        raise ValueError('Influence is not bound to target: %s' % influence)
    direction = str(direction).lower()
    if direction == 'parent':
        relatives = cmds.listRelatives(influence, parent=True, type='joint', fullPath=True) or cmds.listRelatives(influence, parent=True, type='joint') or []
    elif direction == 'child':
        relatives = cmds.listRelatives(influence, children=True, type='joint', fullPath=True) or cmds.listRelatives(influence, children=True, type='joint') or []
    else:
        raise ValueError('Direction must be parent or child: %s' % direction)
    relative = next((joint for joint in relatives if joint in bound), None)
    if not relative:
        raise RuntimeError('%s has no bound %s influence.' % (influence, direction))
    return relative


def unlock_relative_pair(node, influence, direction):
    relative = relative_influence(node, influence, direction)
    unlock_only(node, [influence, relative])
    return [influence, relative]


def unlocked_influences(node):
    return [influence for influence, locked in lock_state(node).items() if not locked]


def next_unlocked(node, current=None):
    unlocked = unlocked_influences(node)
    if not unlocked:
        raise RuntimeError('No unlocked influences found.')
    if current in unlocked:
        return unlocked[(unlocked.index(current) + 1) % len(unlocked)]
    return unlocked[0]


def active_influence(context=None):
    context = paint_state.require_skin_paint_context(context)
    return cmds.artAttrSkinPaintCtx(context, query=True, influence=True)


def set_active_influence(influence, context=None):
    context = paint_state.require_skin_paint_context(context)
    if not cmds.objExists(influence):
        raise RuntimeError('Influence does not exist: %s' % influence)
    cmds.artAttrSkinPaintCtx(context, edit=True, influence=influence)
    return active_influence(context)


def isolate_active(node, context=None):
    influence = active_influence(context)
    if not influence:
        raise RuntimeError('Paint Skin Weights has no active influence')
    return isolate(node, influence)


def _selection_skin_node(items):
    for item in items:
        base = item.split('.', 1)[0]
        if cmds.objExists(base) and cmds.nodeType(base) != 'joint' and skin.find_skin_cluster(base):
            return base
    return None


def unlock_selected_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    node = _selection_skin_node(items)
    joints = cmds.ls(items, type='joint', long=True) or []
    if not node or not joints:
        raise RuntimeError('Select a skinned mesh/component and one or more influence joints.')
    unlock_only(node, joints)
    set_active_influence(joints[0])
    return joints


def unlock_top_two_from_selection():
    vertices = cmds.filterExpand(cmds.ls(selection=True, flatten=True, long=True) or [], selectionMask=31, expand=True) or []
    if not vertices:
        raise RuntimeError('Select one skinned vertex.')
    influences = unlock_top_two(vertices[0])
    set_active_influence(influences[1])
    return influences


def unlock_parent_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    node = _selection_skin_node(items)
    if not node:
        raise RuntimeError('Select a skinned mesh/component while Paint Skin Weights is active.')
    current = active_influence()
    pair = unlock_relative_pair(node, current, 'parent')
    set_active_influence(pair[1])
    return pair


def unlock_child_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    node = _selection_skin_node(items)
    if not node:
        raise RuntimeError('Select a skinned mesh/component while Paint Skin Weights is active.')
    current = active_influence()
    pair = unlock_relative_pair(node, current, 'child')
    set_active_influence(pair[1])
    return pair


def switch_unlocked_from_selection():
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    node = _selection_skin_node(items)
    if not node:
        raise RuntimeError('Select a skinned mesh/component while Paint Skin Weights is active.')
    influence = next_unlocked(node, active_influence())
    return set_active_influence(influence)
