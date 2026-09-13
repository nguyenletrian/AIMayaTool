from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin


def _face_components(faces):
    faces = cmds.ls(faces or [], flatten=True, long=True) or []
    if not faces:
        raise ValueError('At least one polygon face is required')
    mesh = faces[0].split('.', 1)[0]
    if any(face.split('.', 1)[0] != mesh for face in faces):
        raise ValueError('All proxy faces must belong to the same mesh')
    if any('.f[' not in face for face in faces):
        raise ValueError('Proxy extraction requires polygon face components')
    return mesh, faces


def _face_indices(faces):
    indices = []
    for face in faces:
        token = face.rsplit('.f[', 1)[1].rstrip(']')
        if ':' in token:
            start, end = [int(value) for value in token.split(':', 1)]
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(token))
    return sorted(set(indices))


def extract_faces(faces, name=None):
    """Duplicate one mesh and keep only explicit source faces."""
    source_mesh, faces = _face_components(faces)
    duplicate = cmds.duplicate(source_mesh, returnRootsOnly=True, name=name)[0] if name else cmds.duplicate(source_mesh, returnRootsOnly=True)[0]
    face_count = cmds.polyEvaluate(duplicate, face=True)
    keep = set(_face_indices(faces))
    remove = ['%s.f[%d]' % (duplicate, index) for index in range(face_count) if index not in keep]
    if remove:
        cmds.delete(remove)
    cmds.delete(duplicate, constructionHistory=True)
    return duplicate


def bind_like_source(source_mesh, target_mesh):
    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        return None
    influences = skin.influences(source_skin)
    if not influences:
        raise RuntimeError('Source skinCluster has no influences: %s' % source_skin)
    target_skin = skin.find_skin_cluster(target_mesh)
    if not target_skin:
        target_skin = cmds.skinCluster(influences, target_mesh, toSelectedBones=True, normalizeWeights=1, name=target_mesh.split('|')[-1] + '_skinCluster')[0]
    else:
        skin.add_influences(target_skin, influences, weight=0.0, lock_weights=False)
    return target_skin


def copy_skin(source_mesh, target_mesh, surface_association='closestPoint'):
    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        return None
    target_skin = bind_like_source(source_mesh, target_mesh)
    cmds.copySkinWeights(
        sourceSkin=source_skin,
        destinationSkin=target_skin,
        noMirror=True,
        surfaceAssociation=surface_association,
        influenceAssociation=['name', 'closestJoint'],
        normalize=True,
    )
    return target_skin


def create_proxy(faces, name=None, copy_skin_weights=True):
    """Create a proxy mesh from explicit faces and optionally transfer skin weights."""
    source_mesh, faces = _face_components(faces)
    proxy = extract_faces(faces, name=name)
    target_skin = copy_skin(source_mesh, proxy) if copy_skin_weights else None
    return {'source_mesh': source_mesh, 'proxy_mesh': proxy, 'skin_cluster': target_skin}


def create_proxy_from_selection(name=None, copy_skin_weights=True):
    faces = cmds.filterExpand(cmds.ls(selection=True, flatten=True, long=True) or [], selectionMask=34) or []
    if not faces:
        raise RuntimeError('Select one or more polygon faces from a single mesh')
    return create_proxy(faces, name=name, copy_skin_weights=copy_skin_weights)
