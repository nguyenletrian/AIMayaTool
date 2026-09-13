from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _mesh_fn(mesh):
    import maya.api.OpenMaya as om
    selection = om.MSelectionList()
    selection.add(mesh)
    return om.MFnMesh(selection.getDagPath(0))


def component_index(component):
    """Return the integer index from a Maya component string or numeric id."""
    if isinstance(component, (int, float)):
        return int(component)
    return int(str(component).rsplit('[', 1)[-1].split(']', 1)[0])


def vertices_from_edges(mesh, edges, mesh_fn=None):
    """Return sorted vertex component names touched by explicit mesh edges."""
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    vertex_ids = set()
    for edge in edges or []:
        v0, v1 = mesh_fn.getEdgeVertices(component_index(edge))
        vertex_ids.add(v0)
        vertex_ids.add(v1)
    return ['%s.vtx[%d]' % (mesh, vertex_id) for vertex_id in sorted(vertex_ids)]


def is_edge_loop_closed(mesh, edges, mesh_fn=None):
    """Return True when every vertex in the supplied edge set has degree two."""
    edges = list(edges or [])
    if not edges:
        return False
    mesh_fn = mesh_fn or _mesh_fn(mesh)
    counts = {}
    for edge in edges:
        v0, v1 = mesh_fn.getEdgeVertices(component_index(edge))
        counts[v0] = counts.get(v0, 0) + 1
        counts[v1] = counts.get(v1, 0) + 1
    return bool(counts) and all(count == 2 for count in counts.values())


def edges_between(mesh, source_edge, target_edge, selector=None):
    """Return Maya edge components on the ring path, falling back to loop path."""
    selector = selector or _cmds().polySelect
    source_id = component_index(source_edge)
    target_id = component_index(target_edge)
    edge_ids = selector(mesh, edgeRingPath=(source_id, target_id), noSelection=True)
    if edge_ids is None:
        edge_ids = selector(mesh, edgeLoopPath=(source_id, target_id), noSelection=True)
    if edge_ids is None:
        return []
    if isinstance(edge_ids, int):
        edge_ids = [edge_ids]
    return ['%s.e[%d]' % (mesh, edge_id) for edge_id in edge_ids]
