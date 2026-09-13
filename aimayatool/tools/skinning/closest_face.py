from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import geometry


def component_world_position(component):
    values = cmds.xform(component, query=True, worldSpace=True, translation=True)
    if not values or len(values) < 3:
        raise ValueError('Unable to query component position: %s' % component)
    return tuple(values[:3])


def closest_face_for_component(component, target_mesh):
    point = component_world_position(component)
    closest_point, face_index = geometry.closest_point_and_face(target_mesh, point)
    return {
        'component': component,
        'target_mesh': target_mesh,
        'source_point': point,
        'closest_point': closest_point,
        'face_index': face_index,
        'face': '%s.f[%d]' % (str(target_mesh).split('.', 1)[0], face_index),
    }


def match_components_to_mesh(components, target_mesh):
    return [closest_face_for_component(component, target_mesh) for component in components or []]


def match_from_selection():
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if len(selection) < 2:
        raise ValueError('Select one or more source components, then the target mesh last.')
    target_mesh = selection[-1]
    components = selection[:-1]
    if not all('.vtx[' in item or '.cv[' in item or '.pt[' in item for item in components):
        raise ValueError('Source selection must contain point components.')
    return match_components_to_mesh(components, target_mesh)
