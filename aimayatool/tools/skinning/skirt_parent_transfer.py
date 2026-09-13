from __future__ import absolute_import

from . import influence_transfer


def _unique_components(strips):
    result = []
    seen = set()
    for components in (strips or {}).values():
        for component in components or []:
            if component not in seen:
                seen.add(component)
                result.append(component)
    return result


def apply_parent_transfers(skin_cluster, plan, transfer_fn=None, normalize=True):
    """Apply only the parent-to-skirt-joint transfer phase of a composed skirt-parent plan.

    This intentionally does not perform the later adjacent-joint smoothing phase from the
    legacy SkirtParentRun workflow. Each assignment owns explicit perpendicular vertex strips;
    the parent influence weight is moved to that assignment's skirt joint on the union of those
    strip vertices.
    """
    if not skin_cluster:
        raise ValueError('skin_cluster is required')
    if not isinstance(plan, dict):
        raise ValueError('plan must be a dict')
    joint_parent = plan.get('joint_parent')
    if not joint_parent:
        raise ValueError('plan joint_parent is required')
    assignments = list(plan.get('assignments') or [])
    transfer_fn = transfer_fn or influence_transfer.transfer_influence_weight

    applied = []
    for assignment in assignments:
        joint = assignment.get('joint')
        if not joint:
            raise ValueError('assignment joint is required')
        components = _unique_components(assignment.get('strips'))
        changed = transfer_fn(
            skin_cluster,
            components,
            joint_parent,
            joint,
            normalize=normalize,
        ) if components else []
        applied.append({
            'joint': joint,
            'source_influence': joint_parent,
            'components': components,
            'changed': list(changed or []),
        })
    return applied
