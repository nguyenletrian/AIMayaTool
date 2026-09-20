from __future__ import absolute_import

import time
import maya.cmds as cmds

from aimayatool.maya import geometry


def component_world_position(component):
    values = cmds.xform(component, query=True, worldSpace=True, translation=True)
    if not values or len(values) < 3:
        raise ValueError('Unable to query component position: %s' % component)
    return tuple(values[:3])


def closest_face_for_component(component, target_mesh, fn_mesh=None):
    point = component_world_position(component)
    closest_point, face_index = geometry.closest_point_and_face(target_mesh, point, fn_mesh=fn_mesh)
    return {
        'component': component,
        'target_mesh': target_mesh,
        'source_point': point,
        'closest_point': closest_point,
        'face_index': face_index,
        'face': '%s.f[%d]' % (str(target_mesh).split('.', 1)[0], face_index),
    }


def match_components_to_mesh(components, target_mesh):
    components = components or []
    if not components:
        return []
    fn_mesh = geometry.mesh_function(target_mesh)
    return [closest_face_for_component(component, target_mesh, fn_mesh=fn_mesh) for component in components]


def match_from_selection():
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if len(selection) < 2:
        raise ValueError('Select one or more source components, then the target mesh last.')
    target_mesh = selection[-1]
    components = selection[:-1]
    if not all('.vtx[' in item or '.cv[' in item or '.pt[' in item for item in components):
        raise ValueError('Source selection must contain point components.')
    return match_components_to_mesh(components, target_mesh)


def performance_baseline_managed_maya_smoke():
    """Bounded, non-production benchmark for the current closest-face path."""
    target = cmds.polyPlane(name='AIBridgeBaselineTarget', width=20, height=20, subdivisionsX=20, subdivisionsY=20)[0]
    source = cmds.polyPlane(name='AIBridgeBaselineSource', width=10, height=10, subdivisionsX=10, subdivisionsY=10)[0]
    cmds.move(0.25, 1.0, 0.35, source, relative=True)
    components = cmds.ls(source + '.vtx[*]', flatten=True, long=True) or []
    sample = components[:100]
    before = cmds.ls(selection=True, long=True) or []
    start = time.perf_counter()
    results = match_components_to_mesh(sample, target)
    elapsed = time.perf_counter() - start
    valid = len(results) == len(sample) and all(r['face_index'] >= 0 and r['face'].startswith(target + '.f[') for r in results)
    selection_preserved = (cmds.ls(selection=True, long=True) or []) == before
    if not valid or not selection_preserved:
        raise AssertionError('Closest-face baseline changed behavior or selection state')
    evidence = {'operation': 'closest_face_100_vertices', 'sample_count': len(sample), 'elapsed_seconds': elapsed, 'valid_results': valid, 'selection_preserved': selection_preserved}
    print('AIBRIDGE_PERFORMANCE_BASELINE_OK:%s|%.6f' % (len(sample), elapsed))
    return evidence
