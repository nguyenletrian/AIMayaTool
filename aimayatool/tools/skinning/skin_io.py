from __future__ import absolute_import

import json
import os

import maya.cmds as cmds

from aimayatool.maya import skin


_MANIFEST = 'skinData.json'
_QUICK_RELATIVE_DIRECTORY = ('NLTA_Data', 'MeshExport')


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


def _selected_meshes():
    meshes = []
    for node in cmds.ls(selection=True, long=True) or []:
        mesh = skin.mesh_from_component(node)
        if mesh and mesh not in meshes:
            meshes.append(mesh)
    return meshes


def quick_directory(scene_path=None, create=False):
    scene_path = scene_path or cmds.file(query=True, sceneName=True)
    if not scene_path:
        raise RuntimeError('Save the Maya scene before using quick skin IO')
    directory = os.path.join(os.path.dirname(scene_path), *_QUICK_RELATIVE_DIRECTORY)
    return _ensure_directory(directory) if create else os.path.normpath(directory)


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


def import_skin(mesh, directory, preserve_existing=True):
    mesh = skin.mesh_from_component(mesh)
    directory = os.path.normpath(directory)
    if not os.path.isdir(directory):
        raise RuntimeError('Skin data directory does not exist: %s' % directory)

    manifest = _read_manifest(directory)
    key = _mesh_key(mesh)
    item = manifest.get(key)
    if not item:
        raise RuntimeError('No saved skin data found for %s' % mesh)

    filename = item.get('weights_file') or (key + '.xml')
    if not os.path.isfile(os.path.join(directory, filename)):
        raise RuntimeError('Missing skin weights file: %s' % filename)

    existing = skin.find_skin_cluster(mesh)
    if existing and not preserve_existing:
        cmds.delete(existing)

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


def _batch(operation, meshes):
    report = {'succeeded': {}, 'failed': {}}
    for mesh in meshes:
        try:
            report['succeeded'][mesh] = operation(mesh)
        except Exception as exc:
            report['failed'][mesh] = str(exc)
    return report


def export_meshes(meshes, directory):
    directory = _ensure_directory(directory)
    unique_meshes = []
    for node in meshes or []:
        mesh = skin.mesh_from_component(node)
        if mesh and mesh not in unique_meshes:
            unique_meshes.append(mesh)
    if not unique_meshes:
        raise RuntimeError('No meshes supplied for skin export')
    return _batch(lambda mesh: export_skin(mesh, directory), unique_meshes)


def import_meshes(meshes, directory, preserve_existing=True):
    directory = os.path.normpath(directory)
    if not os.path.isdir(directory):
        raise RuntimeError('Skin data directory does not exist: %s' % directory)
    unique_meshes = []
    for node in meshes or []:
        mesh = skin.mesh_from_component(node)
        if mesh and mesh not in unique_meshes:
            unique_meshes.append(mesh)
    if not unique_meshes:
        raise RuntimeError('No meshes supplied for skin import')
    return _batch(
        lambda mesh: import_skin(mesh, directory, preserve_existing=preserve_existing),
        unique_meshes,
    )


def export_selected(directory=None):
    meshes = _selected_meshes()
    if not meshes:
        raise RuntimeError('Select one or more skinned meshes')
    if not directory:
        result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption='Export Skin Data') or []
        if not result:
            return []
        directory = result[0]
    report = export_meshes(meshes, directory)
    if report['failed']:
        raise RuntimeError('Skin export failed: %s' % report['failed'])
    return [report['succeeded'][mesh] for mesh in meshes]


def import_selected(directory=None, preserve_existing=True):
    meshes = _selected_meshes()
    if not meshes:
        raise RuntimeError('Select one or more meshes')
    if not directory:
        result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption='Import Skin Data') or []
        if not result:
            return []
        directory = result[0]
    report = import_meshes(meshes, directory, preserve_existing=preserve_existing)
    if report['failed']:
        raise RuntimeError('Skin import failed: %s' % report['failed'])
    return [report['succeeded'][mesh] for mesh in meshes]


def export_quick_selected():
    return export_selected(quick_directory(create=True))


def import_quick_selected(preserve_existing=True):
    directory = quick_directory(create=False)
    if not os.path.isdir(directory):
        raise RuntimeError('Quick skin data directory does not exist: %s' % directory)
    return import_selected(directory, preserve_existing=preserve_existing)
