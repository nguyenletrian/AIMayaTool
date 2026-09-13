from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import ratio_weights


def _require_component(component, label):
    if not component or '.' not in component:
        raise ValueError('%s must be a mesh component: %s' % (label, component))
    mesh = skin.mesh_from_component(component)
    if not cmds.objExists(mesh):
        raise RuntimeError('%s mesh does not exist: %s' % (label, mesh))
    skin_cluster = skin.find_skin_cluster(mesh)
    if not skin_cluster:
        raise RuntimeError('%s mesh has no skinCluster: %s' % (label, mesh))
    return mesh, skin_cluster


def copy_weights(source_component, target_components, normalize=True):
    """Copy the complete source component weight vector to explicit targets."""
    source_mesh, source_skin = _require_component(source_component, 'Source')
    influences = skin.influences(source_skin)
    if not influences:
        raise RuntimeError('Source skinCluster has no influences: %s' % source_skin)
    source_values = [cmds.skinPercent(source_skin, source_component, query=True, transform=influence) for influence in influences]
    changed = []
    for target in list(target_components or []):
        target_mesh, target_skin = _require_component(target, 'Target')
        if target_mesh != source_mesh or target_skin != source_skin:
            raise ValueError('Component weight copy currently requires source and targets on the same skinned mesh')
        values = list(zip(influences, source_values))
        cmds.skinPercent(target_skin, target, transformValue=values, normalize=normalize)
        changed.append(target)
    return changed


def copy_ratios(source_component, target_components, influences, normalize=True):
    """Copy only the relative proportions of explicit influences to targets."""
    source_mesh, source_skin = _require_component(source_component, 'Source')
    for target in list(target_components or []):
        target_mesh, target_skin = _require_component(target, 'Target')
        if target_mesh != source_mesh or target_skin != source_skin:
            raise ValueError('Component ratio copy currently requires source and targets on the same skinned mesh')
    return ratio_weights.copy_influence_ratios(
        source_skin,
        source_component,
        list(target_components or []),
        list(influences or []),
        normalize=normalize,
    )


def copy_weights_from_selection():
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if len(selection) < 2:
        raise RuntimeError('Select one source component first, then one or more target components')
    return copy_weights(selection[0], selection[1:])


def copy_ratios_from_selection(influences):
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if len(selection) < 2:
        raise RuntimeError('Select one source component first, then one or more target components')
    return copy_ratios(selection[0], selection[1:], influences)
