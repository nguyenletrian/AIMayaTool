from __future__ import absolute_import

from .topology import component_index, edges_between, vertices_from_edges


def _om():
    import maya.api.OpenMaya as om
    return om


def _mesh_fn(mesh):
    om = _om()
    selection = om.MSelectionList()
    selection.add(mesh)
    return om.MFnMesh(selection.getDagPath(0))


def closest_edge_to_point(mesh, edges, point, mesh_fn=None):
    """Return the supplied edge whose world-space center is closest to an explicit point."""
    edges = list(edges or [])
    if not edges:
        return None
    om = _om()
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    target = om.MVector(float(point[0]), float(point[1]), float(point[2]))
    points = mesh_fn.getPoints(om.MSpace.kWorld)
    best_edge = None
    best_distance = float('inf')
    for edge in edges:
        v0, v1 = mesh_fn.getEdgeVertices(component_index(edge))
        p0, p1 = points[v0], points[v1]
        center = om.MVector((p0.x + p1.x) * 0.5, (p0.y + p1.y) * 0.5, (p0.z + p1.z) * 0.5)
        delta = center - target
        distance = delta * delta
        if distance < best_distance:
            best_edge = edge
            best_distance = distance
    return best_edge


def edge_region_between_points(mesh, loop_edges, source_point, target_point, mesh_fn=None, selector=None):
    """Find nearest loop edges to two points, then return the edge path and touched vertices."""
    source_edge = closest_edge_to_point(mesh, loop_edges, source_point, mesh_fn=mesh_fn)
    target_edge = closest_edge_to_point(mesh, loop_edges, target_point, mesh_fn=mesh_fn)
    if source_edge is None or target_edge is None:
        return {'source_edge': source_edge, 'target_edge': target_edge, 'edges': [], 'vertices': []}
    region_edges = edges_between(mesh, source_edge, target_edge, selector=selector)
    return {
        'source_edge': source_edge,
        'target_edge': target_edge,
        'edges': region_edges,
        'vertices': vertices_from_edges(mesh, region_edges, mesh_fn=mesh_fn),
    }
