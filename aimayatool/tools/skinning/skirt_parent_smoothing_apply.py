from __future__ import absolute_import

import math

from .gradient_weights import apply_active_influence_distance_gradient
from .ratio_weights import copy_influence_ratios


def _cmds():
    import maya.cmds as cmds
    return cmds


def _distance_to_joint(component, joint):
    cmds = _cmds()
    point = cmds.pointPosition(component, world=True)
    joint_pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    return math.sqrt(sum((float(point[i]) - float(joint_pos[i])) ** 2 for i in range(3)))


def _targets(source, values):
    result = []
    seen = set([source])
    for value in values or []:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _combined_influence_weight(skin_cluster, component, influences):
    cmds = _cmds()
    return sum(cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influences)


def apply_smoothing_plan(skin_cluster, smoothing_plan, sampler=None, normalize=True, distance_provider=None, gradient_applier=None, ratio_copier=None):
    """Apply legacy-compatible adjacent-joint smoothing from an explicit smoothing plan."""
    if not skin_cluster:
        raise ValueError('skin_cluster is required')
    if not isinstance(smoothing_plan, dict):
        raise ValueError('smoothing_plan is required')
    operations = list(smoothing_plan.get('operations') or [])
    distance_provider = distance_provider or _distance_to_joint
    gradient_applier = gradient_applier or apply_active_influence_distance_gradient
    ratio_copier = ratio_copier or copy_influence_ratios
    applied = []
    for operation in operations:
        influences = list(operation.get('influences') or [])
        active_joint = operation.get('active_joint')
        root_vertices = list(operation.get('root_vertices') or [])
        strips = dict(operation.get('strips') or {})
        if len(influences) != 2 or not active_joint or active_joint not in influences:
            raise ValueError('operation requires two influences and an active_joint in that pair')
        if not root_vertices:
            applied.append({'active_joint': active_joint, 'gradient_vertices': [], 'propagated': {}})
            continue
        distances = [distance_provider(vertex, active_joint) for vertex in root_vertices]
        gradient_changed = gradient_applier(skin_cluster, root_vertices, active_joint, influences, distances, sampler=sampler, normalize=normalize)
        propagated = {}
        for source_vertex in root_vertices:
            targets = _targets(source_vertex, strips.get(source_vertex, []))
            if not targets:
                continue
            if _combined_influence_weight(skin_cluster, source_vertex, influences) <= 1e-12:
                continue
            ratio_copier(skin_cluster, source_vertex, targets, influences, normalize=normalize)
            propagated[source_vertex] = targets
        applied.append({'active_joint': active_joint, 'gradient_vertices': list(gradient_changed or []), 'propagated': propagated})
    return applied
