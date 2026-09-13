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


def _validate_influences(cmds, skin_cluster, influences):
    influences = list(influences or [])
    if not influences:
        raise ValueError("At least one influence is required")
    bound = cmds.skinCluster(skin_cluster, query=True, influence=True) or []
    missing = [influence for influence in influences if influence not in bound]
    if missing:
        raise ValueError("Influence is not bound: {0}".format(missing[0]))
    return influences


def apply_influence_ratios(skin_cluster, components, influences, ratios, normalize=True):
    """Redistribute the current combined weight of explicit influences by ratio."""
    cmds = _cmds()
    components = list(components or [])
    if not components:
        return []
    influences = _validate_influences(cmds, skin_cluster, influences)
    if len(influences) != len(ratios):
        raise ValueError("Influence and ratio counts must match")
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


def _batched_vertex_component(components):
    import maya.api.OpenMaya as om

    cmds = _cmds()
    flat = cmds.ls(list(components or []), flatten=True, long=True) or []
    if not flat:
        return None, None, []
    mesh = None
    indices = []
    for component in flat:
        if '.vtx[' not in component:
            raise ValueError("Batched ratio weighting supports mesh vertices only")
        current_mesh, index_text = component.rsplit('.vtx[', 1)
        index = int(index_text[:-1])
        if mesh is None:
            mesh = current_mesh
        elif current_mesh != mesh:
            raise ValueError("Batched ratio weighting requires vertices from one mesh")
        indices.append(index)

    selection = om.MSelectionList()
    selection.add(mesh)
    dag_path = selection.getDagPath(0)
    component_fn = om.MFnSingleIndexedComponent()
    component_object = component_fn.create(om.MFn.kMeshVertComponent)
    component_fn.addElements(indices)
    return dag_path, component_object, flat


def _skin_fn(skin_cluster):
    import maya.api.OpenMaya as om
    import maya.api.OpenMayaAnim as oma

    selection = om.MSelectionList()
    selection.add(skin_cluster)
    return oma.MFnSkinCluster(selection.getDependNode(0))


def _influence_index(skin_fn, influence):
    import maya.api.OpenMaya as om

    selection = om.MSelectionList()
    selection.add(influence)
    return skin_fn.indexForInfluenceObject(selection.getDagPath(0))


def apply_influence_ratios_batched(skin_cluster, components, influences, ratios):
    """API 2.0 batch variant preserving the selected influences' combined weight."""
    import maya.api.OpenMaya as om

    cmds = _cmds()
    components = list(components or [])
    if not components:
        return []
    influences = _validate_influences(cmds, skin_cluster, influences)
    if len(influences) != len(ratios):
        raise ValueError("Influence and ratio counts must match")
    normalized = _normalized_ratios(ratios)
    dag_path, component_object, flat = _batched_vertex_component(components)
    if not flat:
        return []

    skin_fn = _skin_fn(skin_cluster)
    influence_indices = [_influence_index(skin_fn, influence) for influence in influences]
    per_influence = [skin_fn.getWeights(dag_path, component_object, index) for index in influence_indices]
    values = om.MDoubleArray()
    changed = []
    for component_index, component in enumerate(flat):
        total = sum(weights[component_index] for weights in per_influence)
        if total <= 1e-12:
            values.extend([weights[component_index] for weights in per_influence])
            continue
        values.extend([total * ratio for ratio in normalized])
        changed.append(component)

    skin_fn.setWeights(
        dag_path,
        component_object,
        om.MIntArray(influence_indices),
        values,
        normalize=False,
        returnOldWeights=False,
    )
    return changed


def copy_influence_ratios(skin_cluster, source_component, target_components, influences, normalize=True):
    """Copy normalized influence proportions from one component to explicit targets."""
    cmds = _cmds()
    influences = _validate_influences(cmds, skin_cluster, influences)
    source = [cmds.skinPercent(skin_cluster, source_component, query=True, transform=influence) for influence in influences]
    if sum(source) <= 1e-12:
        raise ValueError("Source component has zero combined influence weight")
    return apply_influence_ratios(skin_cluster, target_components, influences, source, normalize=normalize)
