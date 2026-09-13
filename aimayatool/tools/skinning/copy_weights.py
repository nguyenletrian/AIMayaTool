from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def _require_mesh(node, label):
    mesh = skin.mesh_from_component(node)
    if not mesh or not cmds.objExists(mesh):
        raise RuntimeError('%s mesh does not exist: %s' % (label, node))
    return mesh


def _source_context(source):
    source_mesh = _require_mesh(source, 'Source')
    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        raise RuntimeError('Source has no skinCluster: %s' % source_mesh)
    source_influences = skin.influences(source_skin)
    if not source_influences:
        raise RuntimeError('Source skinCluster has no influences: %s' % source_skin)
    return source_mesh, source_skin, source_influences


def plan_copy_batch(source, targets):
    """Validate a source/target batch without mutating the Maya scene."""
    source_mesh, source_skin, source_influences = _source_context(source)
    targets = list(targets or [])
    if not targets:
        raise ValueError('At least one target mesh is required.')
    plan = []
    seen = set()
    for target in targets:
        target_mesh = _require_mesh(target, 'Target')
        if target_mesh == source_mesh:
            raise ValueError('Source and target meshes must be different.')
        if target_mesh in seen:
            raise ValueError('Duplicate target mesh: %s' % target_mesh)
        seen.add(target_mesh)
        target_skin = skin.find_skin_cluster(target_mesh)
        plan.append({
            'source_mesh': source_mesh,
            'source_skin': source_skin,
            'source_influences': list(source_influences),
            'target_mesh': target_mesh,
            'target_skin': target_skin,
            'will_create_skin': not bool(target_skin),
        })
    return plan


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


def copy_batch(source, targets, surface_association='closestPoint', progress=None):
    """Preflight the complete batch, then copy in order with optional progress callbacks."""
    plan = plan_copy_batch(source, targets)
    total = len(plan)
    copied = []
    for index, item in enumerate(plan, 1):
        target_skin = copy(source, item['target_mesh'], surface_association=surface_association)
        copied.append(target_skin)
        if progress:
            progress(index, total, item['target_mesh'], target_skin)
    return copied


def preview_from_selection():
    items = cmds.ls(selection=True, objectsOnly=True, long=True) or []
    if len(items) < 2:
        raise RuntimeError('Select source mesh first, then one or more target meshes.')
    plan = plan_copy_batch(items[0], items[1:])
    return ['%s -> %s' % (item['target_mesh'], 'create skinCluster' if item['will_create_skin'] else 'reuse skinCluster') for item in plan]


def copy_from_selection():
    items = cmds.ls(selection=True, objectsOnly=True, long=True) or []
    if len(items) < 2:
        raise RuntimeError('Select source mesh first, then one or more target meshes.')
    source = items[0]
    targets = items[1:]
    cmds.progressWindow(title='AIMayaTool Copy Skin', progress=0, maxValue=len(targets), status='Preflight...', isInterruptable=False)
    try:
        def _progress(index, total, target, _target_skin):
            cmds.progressWindow(edit=True, progress=index, status='Copying %d/%d: %s' % (index, total, target.split('|')[-1]))
        return copy_batch(source, targets, progress=_progress)
    finally:
        cmds.progressWindow(endProgress=True)
