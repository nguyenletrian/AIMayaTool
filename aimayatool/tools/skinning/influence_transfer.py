from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def transfer_influence_weight(skin_cluster, components, source_influence, target_influence, normalize=True):
    """Move source influence weight to target influence on explicit components."""
    cmds = _cmds()
    components = list(components or [])
    if not components:
        return []
    influences = cmds.skinCluster(skin_cluster, query=True, influence=True) or []
    if source_influence not in influences:
        raise ValueError("Source influence is not bound: {0}".format(source_influence))
    if target_influence not in influences:
        raise ValueError("Target influence is not bound: {0}".format(target_influence))
    changed = []
    for component in components:
        source_weight = cmds.skinPercent(skin_cluster, component, query=True, transform=source_influence)
        if source_weight <= 0.0:
            continue
        target_weight = cmds.skinPercent(skin_cluster, component, query=True, transform=target_influence)
        cmds.skinPercent(
            skin_cluster,
            component,
            transformValue=[(source_influence, 0.0), (target_influence, target_weight + source_weight)],
            normalize=normalize,
        )
        changed.append(component)
    return changed


def transfer_from_selection():
    """Selection wrapper: source joint, target joint, then mesh components."""
    cmds = _cmds()
    ordered = cmds.ls(orderedSelection=True, flatten=True) or []
    joints = [item for item in ordered if "." not in item and cmds.nodeType(item) == "joint"]
    components = [item for item in ordered if "." in item]
    if len(joints) < 2 or not components:
        raise ValueError("Select source joint, target joint, then one or more skinned components")
    source_influence, target_influence = joints[:2]
    mesh = components[0].split(".", 1)[0]
    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
    skin_clusters = cmds.ls(history, type="skinCluster") or []
    if not skin_clusters:
        raise ValueError("No skinCluster found for {0}".format(mesh))
    return transfer_influence_weight(skin_clusters[0], components, source_influence, target_influence)
