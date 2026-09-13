from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _normalized_ratios(ratios):
    values = [float(value) for value in ratios]
    if not values:
        raise ValueError("At least one ratio is required")
    if any(value < 0.0 for value in values):
        raise ValueError("Ratios must be non-negative")
    total = sum(values)
    if total <= 1e-12:
        raise ValueError("Ratio sum must be greater than zero")
    return [value / total for value in values]


def apply_influence_ratios(skin_cluster, components, influences, ratios, normalize=True):
    """Redistribute the current combined weight of explicit influences by ratio."""
    cmds = _cmds()
    components = list(components or [])
    influences = list(influences or [])
    if not components:
        return []
    if not influences:
        raise ValueError("At least one influence is required")
    if len(influences) != len(ratios):
        raise ValueError("Influence and ratio counts must match")
    bound = cmds.skinCluster(skin_cluster, query=True, influence=True) or []
    missing = [influence for influence in influences if influence not in bound]
    if missing:
        raise ValueError("Influence is not bound: {0}".format(missing[0]))
    normalized = _normalized_ratios(ratios)
    changed = []
    for component in components:
        current = [cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influences]
        total = sum(current)
        if total <= 1e-12:
            continue
        values = [(influence, total * ratio) for influence, ratio in zip(influences, normalized)]
        cmds.skinPercent(skin_cluster, component, transformValue=values, normalize=normalize)
        changed.append(component)
    return changed
