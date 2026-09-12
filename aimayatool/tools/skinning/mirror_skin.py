from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


_MIRROR_PLANES = {
    'x': 'YZ',
    'y': 'XZ',
    'z': 'XY',
}


def _mirror_mode(axis):
    mode = _MIRROR_PLANES.get(str(axis).lower())
    if not mode:
        raise ValueError('axis must be x, y, or z')
    return mode


def mirror(node, axis='x', inverse=False, components=None):
    mesh = skin.mesh_from_component(node)
    if not mesh or not cmds.objExists(mesh):
        raise RuntimeError('Mesh does not exist: %s' % node)

    skin_cluster = skin.find_skin_cluster(mesh)
    if not skin_cluster:
        raise RuntimeError('Target has no skinCluster: %s' % mesh)

    kwargs = {
        'sourceSkin': skin_cluster,
        'destinationSkin': skin_cluster,
        'mirrorMode': _mirror_mode(axis),
        'mirrorInverse': bool(inverse),
        'surfaceAssociation': 'closestPoint',
        'influenceAssociation': ['closestJoint', 'oneToOne'],
    }

    component_list = list(components or [])
    if component_list:
        cmds.select(component_list, replace=True)
        kwargs['selectedComponents'] = True

    cmds.copySkinWeights(**kwargs)
    return skin_cluster


def mirror_from_selection(axis='x', inverse=False):
    items = cmds.ls(selection=True, flatten=True, long=True) or []
    if not items:
        raise RuntimeError('Select a skinned mesh or vertices.')

    first = items[0]
    mesh = skin.mesh_from_component(first)
    components = [item for item in items if '.vtx[' in item and skin.mesh_from_component(item) == mesh]
    return mirror(mesh, axis=axis, inverse=inverse, components=components)
