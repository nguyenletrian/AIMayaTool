from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def _require_mesh(node, label):
    mesh = skin.mesh_from_component(node)
    if not mesh or not cmds.objExists(mesh):
        raise RuntimeError('%s mesh does not exist: %s' % (label, node))
    return mesh


def ensure_target_skin(source_skin, target):
    target_mesh = _require_mesh(target, 'Target')
    source_influences = skin.influences(source_skin)
    if not source_influences:
        raise RuntimeError('Source skinCluster has no influences: %s' % source_skin)

    target_skin = skin.find_skin_cluster(target_mesh)
    if not target_skin:
        target_skin = cmds.skinCluster(
            source_influences,
            target_mesh,
            toSelectedBones=True,
            normalizeWeights=1,
            name=target_mesh.split('|')[-1] + '_skinCluster',
        )[0]
    else:
        skin.add_influences(target_skin, source_influences, weight=0.0, lock_weights=False)
    return target_skin


def copy(source, target, surface_association='closestPoint'):
    source_mesh = _require_mesh(source, 'Source')
    target_mesh = _require_mesh(target, 'Target')
    if source_mesh == target_mesh:
        raise ValueError('Source and target meshes must be different.')

    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        raise RuntimeError('Source has no skinCluster: %s' % source_mesh)
    target_skin = ensure_target_skin(source_skin, target_mesh)

    cmds.copySkinWeights(
        sourceSkin=source_skin,
        destinationSkin=target_skin,
        noMirror=True,
        surfaceAssociation=surface_association,
        influenceAssociation=['name', 'closestJoint'],
        normalize=True,
    )
    return target_skin


def copy_from_selection():
    items = cmds.ls(selection=True, objectsOnly=True, long=True) or []
    if len(items) < 2:
        raise RuntimeError('Select source mesh first, then one or more target meshes.')
    source = items[0]
    return [copy(source, target) for target in items[1:]]
