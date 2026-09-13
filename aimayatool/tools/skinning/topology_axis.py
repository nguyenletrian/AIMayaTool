from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _om():
    import maya.api.OpenMaya as om
    return om


def _dag_path(node):
    om = _om()
    selection = om.MSelectionList()
    selection.add(node)
    return selection.getDagPath(0)


def connected_edges(mesh, vertex_index):
    om = _om()
    iterator = om.MItMeshVertex(_dag_path(mesh))
    iterator.setIndex(int(vertex_index))
    return list(iterator.getConnectedEdges())


def joint_x_axis(joint):
    matrix = _cmds().xform(joint, query=True, worldSpace=True, matrix=True)
    return (float(matrix[0]), float(matrix[1]), float(matrix[2]))


def choose_edge_by_axis(edge_vectors, axis, perpendicular=False):
    """Choose an edge id by absolute normalized dot against an explicit axis."""
    import math
    ax = [float(v) for v in axis]
    length = math.sqrt(sum(v * v for v in ax))
    if length <= 1e-12:
        raise ValueError('axis must be non-zero')
    ax = [v / length for v in ax]
    best_id = None
    best_score = float('inf') if perpendicular else -1.0
    for edge_id, vector in edge_vectors:
        vec = [float(v) for v in vector]
        vec_len = math.sqrt(sum(v * v for v in vec))
        if vec_len <= 1e-12:
            continue
        score = abs(sum(ax[i] * (vec[i] / vec_len) for i in range(3)))
        if (perpendicular and score < best_score) or (not perpendicular and score > best_score):
            best_id, best_score = int(edge_id), score
    return best_id


def best_edge_by_joint_axis(mesh, joint, vertex_index, perpendicular=False):
    """Choose the connected edge most parallel/perpendicular to the joint X axis."""
    om = _om()
    dag = _dag_path(mesh)
    iterator = om.MItMeshEdge(dag)
    vectors = []
    for edge_id in connected_edges(mesh, vertex_index):
        iterator.setIndex(edge_id)
        p0 = iterator.point(0, om.MSpace.kWorld)
        p1 = iterator.point(1, om.MSpace.kWorld)
        vectors.append((edge_id, (p1.x - p0.x, p1.y - p0.y, p1.z - p0.z)))
    return choose_edge_by_axis(vectors, joint_x_axis(joint), perpendicular=perpendicular)
