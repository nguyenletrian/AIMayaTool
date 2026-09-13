from __future__ import absolute_import

import re

import maya.cmds as cmds


_SET_PREFIX = 'AIMayaToolSkinSet_'


def _base_name(node):
    node = (node or '').split('.', 1)[0]
    node = node.split('|')[-1].split(':')[-1]
    if not node:
        raise ValueError('Cannot derive selection-set family from empty node')
    return re.sub(r'[^A-Za-z0-9_]+', '_', node)


def family_prefix(node):
    return _SET_PREFIX + _base_name(node) + '_'


def family_prefix_from_selection(selection=None):
    selection = list(selection if selection is not None else (cmds.ls(selection=True, long=True) or []))
    if not selection:
        raise RuntimeError('Select a mesh, component, or member of the desired set family')
    return family_prefix(selection[0])


def family_sets(prefix):
    result = []
    pattern = re.compile(r'^%s(\d+)$' % re.escape(prefix))
    for object_set in cmds.ls(type='objectSet') or []:
        match = pattern.match(object_set)
        if match:
            result.append((int(match.group(1)), object_set))
    return [name for _, name in sorted(result)]


def create_from_selection(selection=None):
    selection = list(selection if selection is not None else (cmds.ls(selection=True, long=True) or []))
    if not selection:
        raise RuntimeError('Select one or more objects/components before creating a set')
    prefix = family_prefix(selection[0])
    existing = family_sets(prefix)
    indices = [int(name[len(prefix):]) for name in existing]
    next_index = (max(indices) + 1) if indices else 0
    object_set = cmds.sets(name='%s%03d' % (prefix, next_index), empty=True)
    cmds.sets(selection, add=object_set)
    return object_set


def members(object_set):
    return cmds.sets(object_set, query=True) or []


def _member_visible(member):
    node = member.split('.', 1)[0]
    if not cmds.objExists(node):
        return False
    try:
        return bool(cmds.getAttr(node + '.visibility'))
    except Exception:
        return True


def visible_index(prefix):
    sets = family_sets(prefix)
    if not sets:
        return None
    visible = []
    for index, object_set in enumerate(sets):
        set_members = members(object_set)
        if set_members and all(_member_visible(member) for member in set_members):
            visible.append(index)
    return visible[0] if len(visible) == 1 else None


def show_index(prefix, index):
    sets = family_sets(prefix)
    if not sets:
        raise RuntimeError('No selection sets found for family: %s' % prefix)
    index = int(index) % len(sets)
    for current_index, object_set in enumerate(sets):
        set_members = members(object_set)
        if not set_members:
            continue
        if current_index == index:
            cmds.showHidden(set_members)
        else:
            cmds.hide(set_members)
    return index, sets[index]


def cycle(prefix, step=1, current_index=None):
    sets = family_sets(prefix)
    if not sets:
        raise RuntimeError('No selection sets found for family: %s' % prefix)
    if current_index is None:
        current_index = visible_index(prefix)
    if current_index is None:
        target = 0 if step >= 0 else len(sets) - 1
    else:
        target = (int(current_index) + int(step)) % len(sets)
    return show_index(prefix, target)


def next_from_selection(current_index=None):
    return cycle(family_prefix_from_selection(), 1, current_index=current_index)


def previous_from_selection(current_index=None):
    return cycle(family_prefix_from_selection(), -1, current_index=current_index)


def delete_family(prefix, restore_visibility=True):
    deleted = []
    for object_set in family_sets(prefix):
        set_members = members(object_set)
        if restore_visibility and set_members:
            cmds.showHidden(set_members)
        cmds.delete(object_set)
        deleted.append(object_set)
    return deleted


def delete_from_selection(restore_visibility=True):
    return delete_family(family_prefix_from_selection(), restore_visibility=restore_visibility)
