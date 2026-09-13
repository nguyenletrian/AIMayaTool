from __future__ import absolute_import

from . import loop_groups


def build_smoothing_plan(plan, mesh_fn=None, selector=None, group_builder=None):
    """Build explicit non-mutating adjacent-joint smoothing operations from a skirt-parent plan."""
    if not isinstance(plan, dict):
        raise ValueError('plan is required')
    mesh = plan.get('mesh')
    if not mesh:
        raise ValueError('plan mesh is required')
    spans = list(plan.get('spans') or [])
    group_builder = group_builder or loop_groups.group_vertices_by_perpendicular_loops
    operations = []
    for span in spans:
        source_joint = span.get('source_joint')
        target_joint = span.get('target_joint')
        vertices = list(span.get('vertices') or [])
        if not source_joint or not target_joint:
            raise ValueError('span source_joint and target_joint are required')
        strips = group_builder(mesh, vertices, mesh_fn=mesh_fn, selector=selector) if vertices else {}
        operations.append({
            'source_joint': source_joint,
            'target_joint': target_joint,
            'active_joint': target_joint,
            'influences': [source_joint, target_joint],
            'root_vertices': vertices,
            'strips': strips,
        })
    return {
        'mesh': mesh,
        'joint_parent': plan.get('joint_parent'),
        'closed': bool(plan.get('closed')),
        'operations': operations,
    }
