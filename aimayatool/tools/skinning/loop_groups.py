from __future__ import absolute_import

from .topology import component_index, vertices_from_edges


def _cmds():
    import maya.cmds as cmds
    return cmds


def _mesh_fn(mesh):
    import maya.api.OpenMaya as om
    selection = om.MSelectionList()
    selection.add(mesh)
    return om.MFnMesh(selection.getDagPath(0))


def _xyz(value):
    return (float(value[0]), float(value[1]), float(value[2])) if hasattr(value, '__getitem__') else (float(value.x), float(value.y), float(value.z))


def _direction(a, b):
    ax, ay, az = _xyz(a)
    bx, by, bz = _xyz(b)
    vector = (bx - ax, by - ay, bz - az)
    length_sq = sum(value * value for value in vector)
    if length_sq == 0.0:
        return None
    length = length_sq ** 0.5
    return tuple(value / length for value in vector)


def connected_vertices_in_set(mesh, vertex, vertices, mesh_fn=None):
    """Return connected target vertices and their edges, limited to an explicit vertex set."""
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    source_id = component_index(vertex)
    allowed = {component_index(item) for item in vertices or []}
    result = []
    for edge_id in range(mesh_fn.numEdges):
        v0, v1 = mesh_fn.getEdgeVertices(edge_id)
        if v0 == source_id:
            other = v1
        elif v1 == source_id:
            other = v0
        else:
            continue
        if other in allowed:
            result.append((vertex, '%s.vtx[%d]' % (mesh, other), '%s.e[%d]' % (mesh, edge_id)))
    return result


def perpendicular_edge_from_vertices(mesh, source_vertex, target_vertex, threshold=0.25, mesh_fn=None):
    """Return the connected edge at source most perpendicular to source->target."""
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    points = mesh_fn.getPoints()
    source_id = component_index(source_vertex)
    target_id = component_index(target_vertex)
    reference = _direction(points[source_id], points[target_id])
    if reference is None:
        return None
    best_edge = None
    best_score = float('inf')
    for edge_id in range(mesh_fn.numEdges):
        v0, v1 = mesh_fn.getEdgeVertices(edge_id)
        if v0 == source_id:
            other = v1
        elif v1 == source_id:
            other = v0
        else:
            continue
        if other == target_id:
            continue
        direction = _direction(points[source_id], points[other])
        if direction is None:
            continue
        score = abs(sum(reference[index] * direction[index] for index in range(3)))
        if score < best_score:
            best_score = score
            best_edge = edge_id
    if best_edge is None or best_score > float(threshold):
        return None
    return '%s.e[%d]' % (mesh, best_edge)


def edge_loop_vertices(mesh, edge, mesh_fn=None, selector=None):
    """Expand an explicit edge to its Maya edge loop and return touched vertices."""
    selector = selector or _cmds().polySelect
    edge_ids = selector(mesh, edgeLoop=component_index(edge), noSelection=True)
    if not edge_ids:
        return []
    if isinstance(edge_ids, int):
        edge_ids = [edge_ids]
    return vertices_from_edges(mesh, ['%s.e[%d]' % (mesh, edge_id) for edge_id in edge_ids], mesh_fn=mesh_fn)


def group_vertices_by_perpendicular_loops(mesh, vertices, threshold=0.25, mesh_fn=None, selector=None):
    """Map each explicit root-loop vertex to the perpendicular edge-loop vertex strip through it."""
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    vertices = list(vertices or [])
    result = {}
    for vertex in vertices:
        for source, target, _ in connected_vertices_in_set(mesh, vertex, vertices, mesh_fn=mesh_fn):
            edge = perpendicular_edge_from_vertices(mesh, source, target, threshold=threshold, mesh_fn=mesh_fn)
            if edge is not None:
                result[vertex] = edge_loop_vertices(mesh, edge, mesh_fn=mesh_fn, selector=selector)
    return result
