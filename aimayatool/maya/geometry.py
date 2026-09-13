from __future__ import absolute_import

import maya.api.OpenMaya as om
import maya.cmds as cmds


def _mesh_dag_path(mesh):
    if not mesh:
        raise ValueError('mesh is required')
    node = str(mesh).split('.', 1)[0]
    if not cmds.objExists(node):
        raise ValueError('Mesh does not exist: %s' % node)
    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
    shape = shapes[0] if shapes else node
    if cmds.nodeType(shape) != 'mesh':
        raise ValueError('Expected mesh transform or shape: %s' % mesh)
    selection = om.MSelectionList()
    selection.add(shape)
    return selection.getDagPath(0)


def closest_point_and_face(mesh, point, space=om.MSpace.kWorld):
    """Return ((x, y, z), face_index) for the closest point on a polygon mesh."""
    dag = _mesh_dag_path(mesh)
    fn_mesh = om.MFnMesh(dag)
    query = om.MPoint(float(point[0]), float(point[1]), float(point[2]))
    closest, face_index = fn_mesh.getClosestPoint(query, space)
    return (closest.x, closest.y, closest.z), int(face_index)


def closest_face(mesh, point, space=om.MSpace.kWorld):
    return closest_point_and_face(mesh, point, space=space)[1]
