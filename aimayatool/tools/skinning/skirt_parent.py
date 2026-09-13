from __future__ import absolute_import

from . import joint_regions, loop_groups
from .topology import is_edge_loop_closed, vertices_from_edges
from .topology_region import edge_region_between_points


def _mesh_fn(mesh):
    import maya.api.OpenMaya as om
    selection = om.MSelectionList()
    selection.add(mesh)
    return om.MFnMesh(selection.getDagPath(0))


def _world_vertex_positions(mesh, vertices, mesh_fn=None):
    import maya.api.OpenMaya as om
    from .topology import component_index
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    points = mesh_fn.getPoints(om.MSpace.kWorld)
    return {vertex: (points[component_index(vertex)].x, points[component_index(vertex)].y, points[component_index(vertex)].z) for vertex in vertices}


def build_skirt_parent_plan(mesh, joint_parent, joints, root_loop, joint_positions=None, root_vertex_positions=None, mesh_fn=None, selector=None, group_builder=None, radius_scale=0.6, clockwise=False):
    """Compose proven topology primitives into an explicit, non-mutating skirt-parent plan."""
    joints = list(joints or [])
    root_loop = list(root_loop or [])
    if not joint_parent:
        raise ValueError('joint_parent is required')
    if len(joints) < 2:
        raise ValueError('at least two skirt joints are required')
    if not root_loop:
        raise ValueError('root_loop is required')
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    joint_positions = joint_positions or joint_regions.joint_positions(joints)
    ordered = joint_regions.circular_order(joints, joint_positions, clockwise=clockwise)
    root_vertices = vertices_from_edges(mesh, root_loop, mesh_fn=mesh_fn)
    root_vertex_positions = root_vertex_positions or _world_vertex_positions(mesh, root_vertices, mesh_fn=mesh_fn)
    group_builder = group_builder or loop_groups.group_vertices_by_perpendicular_loops

    assignments = []
    for joint in ordered:
        nearest = joint_regions.closest_items(joint, joint_positions, count=1)
        if not nearest:
            continue
        radius = nearest[0][1] * float(radius_scale)
        center = joint_positions[joint]
        affected = [vertex for vertex in root_vertices if vertex in root_vertex_positions and sum((float(root_vertex_positions[vertex][axis]) - float(center[axis])) ** 2 for axis in range(3)) <= radius * radius]
        strips = group_builder(mesh, affected, mesh_fn=mesh_fn, selector=selector) if affected else {}
        assignments.append({'joint': joint, 'nearest_joint': nearest[0][0], 'radius': radius, 'root_vertices': affected, 'strips': strips})

    closed = is_edge_loop_closed(mesh, root_loop, mesh_fn=mesh_fn)
    pairs = [(ordered[index], ordered[index + 1]) for index in range(len(ordered) - 1)]
    if closed and len(ordered) > 2:
        pairs.append((ordered[-1], ordered[0]))
    spans = []
    for source_joint, target_joint in pairs:
        region = edge_region_between_points(mesh, root_loop, joint_positions[source_joint], joint_positions[target_joint], mesh_fn=mesh_fn, selector=selector)
        spans.append({'source_joint': source_joint, 'target_joint': target_joint, 'source_edge': region['source_edge'], 'target_edge': region['target_edge'], 'edges': region['edges'], 'vertices': region['vertices']})

    return {'mesh': mesh, 'joint_parent': joint_parent, 'joints': ordered, 'root_loop': root_loop, 'root_vertices': root_vertices, 'closed': closed, 'assignments': assignments, 'spans': spans}
