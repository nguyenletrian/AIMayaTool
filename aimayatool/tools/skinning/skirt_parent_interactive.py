from __future__ import absolute_import

from aimayatool.maya import skin

from .skirt_parent_workflow import run_skirt_parent_workflow


def _cmds():
    import maya.cmds as cmds
    return cmds


def context_from_selection(selection=None):
    cmds = _cmds()
    items = list(selection) if selection is not None else (cmds.ls(selection=True, flatten=True) or [])
    joints = []
    root_loop = []
    for item in items:
        node = item.split('.', 1)[0]
        if '.e[' in item:
            root_loop.append(item)
        elif cmds.objExists(node) and cmds.nodeType(node) == 'joint':
            joints.append(node)
    if len(joints) < 2:
        raise RuntimeError('Select the parent joint first, then two or more skirt joints.')
    if not root_loop:
        raise RuntimeError('Select the skirt root edge loop together with the joints.')
    meshes = []
    for edge in root_loop:
        mesh = edge.split('.', 1)[0]
        if mesh not in meshes:
            meshes.append(mesh)
    if len(meshes) != 1:
        raise RuntimeError('Selected root-loop edges must belong to one mesh.')
    data = skin.skin_data(meshes[0])
    if not data['skin_cluster']:
        raise RuntimeError('Selected root-loop mesh has no skinCluster.')
    parent = joints[0]
    skirt_joints = joints[1:]
    bound = set(data['influences'] or [])
    missing = [joint for joint in [parent] + skirt_joints if joint not in bound]
    if missing:
        raise RuntimeError('Selected joint is not an influence of the skinCluster: %s' % missing[0])
    return {
        'mesh': data['mesh'],
        'skin_cluster': data['skin_cluster'],
        'joint_parent': parent,
        'joints': skirt_joints,
        'root_loop': root_loop,
    }


def run_from_selection(selection=None, normalize=True):
    context = context_from_selection(selection=selection)
    return run_skirt_parent_workflow(
        context['mesh'],
        context['skin_cluster'],
        context['joint_parent'],
        context['joints'],
        context['root_loop'],
        normalize=normalize,
    )
