from __future__ import absolute_import

from .gradient_profile import sample_distance_profile


def _cmds():
    import maya.cmds as cmds
    return cmds


def apply_active_influence_distance_gradient(skin_cluster, components, active_influence, influence_group, distances, sampler=None, normalize=True):
    """Set one active influence from inverse-distance profile values over an explicit influence group.

    For each component, the target active-influence weight is:
        sum(current weights in influence_group) * sampled_profile_value

    Only the active influence is written explicitly; Maya handles normalization when normalize=True,
    matching the useful core behavior of the legacy GradientActiveJoint workflow without selection,
    envelope, timeline, or UI side effects.
    """
    cmds = _cmds()
    components = list(components or [])
    influence_group = list(influence_group or [])
    distances = list(distances or [])
    if not components:
        return []
    if len(components) != len(distances):
        raise ValueError("Component and distance counts must match")
    if not influence_group:
        raise ValueError("At least one influence is required")
    if active_influence not in influence_group:
        raise ValueError("Active influence must belong to influence_group")
    bound = cmds.skinCluster(skin_cluster, query=True, influence=True) or []
    for influence in influence_group:
        if influence not in bound:
            raise ValueError("Influence is not bound: {0}".format(influence))
    values = sample_distance_profile(distances, sampler=sampler)
    changed = []
    for component, profile_value in zip(components, values):
        total = sum(cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influence_group)
        if total <= 1e-12:
            continue
        target = total * profile_value
        cmds.skinPercent(skin_cluster, component, transformValue=[(active_influence, target)], normalize=normalize)
        changed.append(component)
    return changed
