from __future__ import absolute_import

from .gradient_profile import sample_distance_profile


def _cmds():
    import maya.cmds as cmds
    return cmds


def _validate_inputs(cmds, skin_cluster, components, active_influence, influence_group, distances):
    components = list(components or [])
    influence_group = list(influence_group or [])
    distances = list(distances or [])
    if not components:
        return components, influence_group, distances
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
    return components, influence_group, distances


def _apply_active_influence_distance_gradient_legacy(skin_cluster, components, active_influence, influence_group, values, normalize=True):
    cmds = _cmds()
    changed = []
    for component, profile_value in zip(components, values):
        total = sum(cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influence_group)
        if total <= 1e-12:
            continue
        cmds.skinPercent(skin_cluster, component, transformValue=[(active_influence, total * profile_value)], normalize=normalize)
        changed.append(component)
    return changed


def apply_active_influence_distance_gradient(skin_cluster, components, active_influence, influence_group, distances, sampler=None, normalize=True):
    """Set one active influence from inverse-distance profile values over an explicit influence group."""
    cmds = _cmds()
    components, influence_group, distances = _validate_inputs(
        cmds, skin_cluster, components, active_influence, influence_group, distances
    )
    if not components:
        return []
    values = sample_distance_profile(distances, sampler=sampler)
    return _apply_active_influence_distance_gradient_legacy(
        skin_cluster, components, active_influence, influence_group, values, normalize=normalize
    )


def _batched_vertex_component(components):
    import maya.api.OpenMaya as om

    cmds = _cmds()
    report_components = list(components or [])
    flat = cmds.ls(report_components, flatten=True, long=True) or []
    if not flat:
        return None, None, [], []
    if len(report_components) != len(flat):
        raise ValueError("Batched gradient weighting requires one explicit vertex per input component")
    mesh = None
    indices = []
    for component in flat:
        if '.vtx[' not in component:
            raise ValueError("Batched gradient weighting supports mesh vertices only")
        current_mesh, index_text = component.rsplit('.vtx[', 1)
        index = int(index_text[:-1])
        if mesh is None:
            mesh = current_mesh
        elif current_mesh != mesh:
            raise ValueError("Batched gradient weighting requires vertices from one mesh")
        indices.append(index)
    selection = om.MSelectionList()
    selection.add(mesh)
    dag_path = selection.getDagPath(0)
    component_fn = om.MFnSingleIndexedComponent()
    component_object = component_fn.create(om.MFn.kMeshVertComponent)
    component_fn.addElements(indices)
    return dag_path, component_object, flat, report_components


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


def apply_active_influence_distance_gradient_batched(skin_cluster, components, active_influence, influence_group, distances, sampler=None, normalize=True):
    """API 2.0 batch candidate preserving legacy caller-facing changed-component reporting."""
    import maya.api.OpenMaya as om

    cmds = _cmds()
    components, influence_group, distances = _validate_inputs(
        cmds, skin_cluster, components, active_influence, influence_group, distances
    )
    if not components:
        return []
    profile_values = sample_distance_profile(distances, sampler=sampler)
    dag_path, component_object, flat, report_components = _batched_vertex_component(components)
    if not flat:
        return []
    skin_fn = _skin_fn(skin_cluster)
    group_indices = [_influence_index(skin_fn, influence) for influence in influence_group]
    active_index = _influence_index(skin_fn, active_influence)
    per_influence = [skin_fn.getWeights(dag_path, component_object, index) for index in group_indices]
    target_values = []
    changed = []
    for component_index, (component, profile_value) in enumerate(zip(report_components, profile_values)):
        total = sum(weights[component_index] for weights in per_influence)
        if total <= 1e-12:
            target_values.append(per_influence[group_indices.index(active_index)][component_index])
            continue
        target_values.append(total * profile_value)
        changed.append(component)
    skin_fn.setWeights(
        dag_path,
        component_object,
        om.MIntArray([active_index]),
        om.MDoubleArray(target_values),
        normalize=normalize,
        returnOldWeights=False,
    )
    return changed
