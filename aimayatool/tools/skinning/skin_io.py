from __future__ import absolute_import

import json
import os

import maya.cmds as cmds

from aimayatool.maya import skin


_MANIFEST = 'skinData.json'


def _mesh_key(mesh):
    return (mesh or '').replace('|', '&').replace(':', '%')


def _ensure_directory(directory):
    if not directory:
        raise RuntimeError('Skin data directory is required')
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return os.path.normpath(directory)


def _manifest_path(directory):
    return os.path.join(directory, _MANIFEST)


def _read_manifest(directory):
    path = _manifest_path(directory)
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as stream:
        return json.load(stream)


def _write_manifest(directory, data):
    path = _manifest_path(directory)
    with open(path, 'w') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
    return path


def export_skin(mesh, directory):
    mesh = skin.mesh_from_component(mesh)
    skin_cluster = skin.find_skin_cluster(mesh)
    if not skin_cluster:
        raise RuntimeError('No skinCluster found on %s' % mesh)

    directory = _ensure_directory(directory)
    key = _mesh_key(mesh)
    filename = key + '.xml'
    cmds.deformerWeights(
        filename,
        export=True,
        deformer=skin_cluster,
        path=directory,
        format='XML',
    )

    manifest = _read_manifest(directory)
    manifest[key] = {
        'mesh': mesh,
        'skin_cluster': skin_cluster,
        'influences': list(skin.influences(skin_cluster)),
        'weights_file': filename,
    }
    _write_manifest(directory, manifest)
    return os.path.join(directory, filename)


def _ensure_skin_cluster(mesh, item):
    existing = skin.find_skin_cluster(mesh)
    influence_names = [name for name in item.get('influences', []) if cmds.objExists(name)]
    if not influence_names:
        raise RuntimeError('No saved influences exist in the current scene for %s' % mesh)

    if existing:
        missing = [joint for joint in influence_names if joint not in skin.influences(existing)]
        skin.add_influences(existing, missing, weight=0.0, lock_weights=False)
        return existing

    desired_name = item.get('skin_cluster') or (mesh.split('|')[-1] + '_skinCluster')
    return cmds.skinCluster(
        influence_names,
        mesh,
        toSelectedBones=True,
        normalizeWeights=1,
        name=desired_name,
    )[0]


def import_skin(mesh, directory):
    mesh = skin.mesh_from_component(mesh)
    directory = os.path.normpath(directory)
    manifest = _read_manifest(directory)
    key = _mesh_key(mesh)
    item = manifest.get(key)
    if not item:
        raise RuntimeError('No saved skin data found for %s' % mesh)

    filename = item.get('weights_file') or (key + '.xml')
    if not os.path.isfile(os.path.join(directory, filename)):
        raise RuntimeError('Missing skin weights file: %s' % filename)

    skin_cluster = _ensure_skin_cluster(mesh, item)
    cmds.deformerWeights(
        filename,
        im=True,
        method='index',
        deformer=skin_cluster,
        path=directory,
    )
    cmds.skinCluster(skin_cluster, edit=True, forceNormalizeWeights=True)
    return skin_cluster


def export_selected(directory=None):
    meshes = []
    for node in cmds.ls(selection=True, long=True) or []:
        mesh = skin.mesh_from_component(node)
        if mesh not in meshes:
            meshes.append(mesh)
    if not meshes:
        raise RuntimeError('Select one or more skinned meshes')
    if not directory:
        result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption='Export Skin Data') or []
        if not result:
            return []
        directory = result[0]
    return [export_skin(mesh, directory) for mesh in meshes]


def import_selected(directory=None):
    meshes = []
    for node in cmds.ls(selection=True, long=True) or []:
        mesh = skin.mesh_from_component(node)
        if mesh not in meshes:
            meshes.append(mesh)
    if not meshes:
        raise RuntimeError('Select one or more meshes')
    if not directory:
        result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption='Import Skin Data') or []
        if not result:
            return []
        directory = result[0]
    return [import_skin(mesh, directory) for mesh in meshes]
