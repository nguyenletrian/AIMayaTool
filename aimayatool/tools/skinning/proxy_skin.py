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


def _axis_index(axis):
    axis = str(axis).lower()
    if axis not in ('x', 'y', 'z'):
        raise ValueError('Axis must be x, y, or z: %s' % axis)
    return ('x', 'y', 'z').index(axis)


def _region_axis_direction(faces, axis):
    index = _axis_index(axis)
    bounds = cmds.exactWorldBoundingBox(faces)
    center = (bounds[index] + bounds[index + 3]) * 0.5
    return 0 if center < 0.0 else 1


def _mesh_transform(node):
    node = (cmds.ls(node, long=True) or [node])[0]
    if '.' in node:
        node = node.split('.', 1)[0]
    if cmds.nodeType(node) == 'mesh':
        parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
        if not parents:
            raise RuntimeError('Mesh shape has no transform: %s' % node)
        node = parents[0]
    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
    if not any(cmds.nodeType(shape) == 'mesh' for shape in shapes):
        raise ValueError('Expected polygon mesh: %s' % node)
    return node


def _vertex_components(items):
    items = cmds.ls(items or [], flatten=True, long=True) or []
    if not items:
        raise ValueError('At least one mesh or vertex component is required')
    vertices = cmds.filterExpand(items, selectionMask=31, expand=True) or []
    if vertices:
        vertices = cmds.ls(vertices, flatten=True, long=True) or []
        meshes = sorted(set(vertex.split('.', 1)[0] for vertex in vertices))
        if len(meshes) != 1:
            raise ValueError('Vertex components must belong to one mesh')
        return meshes[0], vertices
    if len(items) != 1:
        raise ValueError('Use one mesh transform or explicit vertices')
    mesh = _mesh_transform(items[0])
    vertices = cmds.ls(mesh + '.vtx[*]', flatten=True, long=True) or []
    if not vertices:
        raise RuntimeError('Mesh has no vertices: %s' % mesh)
    return mesh, vertices


def _closest_source_vertex(source_vertices, target_vertex):
    target_position = cmds.pointPosition(target_vertex, world=True)
    closest = None
    closest_distance = None
    for source_vertex in source_vertices:
        source_position = cmds.pointPosition(source_vertex, world=True)
        distance = sum((source_position[index] - target_position[index]) ** 2 for index in range(3))
        if closest_distance is None or distance < closest_distance:
            closest = source_vertex
            closest_distance = distance
    return closest


def _copy_selected_skin_weights_legacy(source_skin, target_skin, source_vertices, target_vertices):
    """Compatibility fallback for Maya builds before copySkinWeights -selectedComponents."""
    source_influences = skin.influences(source_skin)
    for target_vertex in target_vertices:
        source_vertex = _closest_source_vertex(source_vertices, target_vertex)
        values = [(influence, cmds.skinPercent(source_skin, source_vertex, query=True, transform=influence)) for influence in source_influences]
        cmds.skinPercent(target_skin, target_vertex, transformValue=values, normalize=True)


def _copy_selected_skin_weights(source_skin, target_skin, source_vertices, target_vertices, surface_association):
    cmds.select(source_vertices, replace=True)
    cmds.select(target_vertices, add=True)
    try:
        cmds.copySkinWeights(
            sourceSkin=source_skin,
            destinationSkin=target_skin,
            noMirror=True,
            surfaceAssociation=surface_association,
            influenceAssociation=['closestJoint', 'oneToOne'],
            selectedComponents=True,
            normalize=True,
        )
        return 'copySkinWeights:selectedComponents'
    except TypeError as exc:
        if 'selectedComponents' not in str(exc):
            raise
    _copy_selected_skin_weights_legacy(source_skin, target_skin, source_vertices, target_vertices)
    return 'legacy:closestSelectedVertex'


def extract_faces(faces, name=None):
    """Duplicate one mesh and keep only explicit source faces and mesh shapes."""
    source_mesh, faces = _face_components(faces)
    duplicate = cmds.duplicate(source_mesh, returnRootsOnly=True, name=name)[0] if name else cmds.duplicate(source_mesh, returnRootsOnly=True)[0]
    children = cmds.listRelatives(duplicate, children=True, fullPath=True) or []
    extra_children = [child for child in children if cmds.nodeType(child) != 'mesh']
    if extra_children:
        cmds.delete(extra_children)
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
        target_skin = cmds.skinCluster(
            influences,
            target_mesh,
            normalizeWeights=1,
            name=target_mesh.split('|')[-1] + '_skinCluster',
        )[0]
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


def capture_proxy_snapshot(source):
    """Capture an explicit proxy skin source without storing module-global session state."""
    source_mesh, vertices = _vertex_components(source if isinstance(source, (list, tuple)) else [source])
    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        raise RuntimeError('Proxy snapshot source is not skinned: %s' % source_mesh)
    return {'source_mesh': source_mesh, 'source_vertices': list(vertices)}


def paste_proxy_snapshot(snapshot, targets, surface_association='closestPoint'):
    """Transfer a captured proxy snapshot to explicit target meshes or vertex components."""
    if not isinstance(snapshot, dict) or not snapshot.get('source_mesh') or not snapshot.get('source_vertices'):
        raise ValueError('Invalid proxy snapshot')
    source_mesh = _mesh_transform(snapshot['source_mesh'])
    source_vertices = cmds.ls(snapshot['source_vertices'], flatten=True, long=True) or []
    if not source_vertices:
        raise RuntimeError('Proxy snapshot source vertices no longer exist')
    source_skin = skin.find_skin_cluster(source_mesh)
    if not source_skin:
        raise RuntimeError('Proxy snapshot source skinCluster no longer exists: %s' % source_mesh)

    raw_targets = cmds.ls(targets if isinstance(targets, (list, tuple)) else [targets], flatten=True, long=True) or []
    if not raw_targets:
        raise ValueError('At least one proxy paste target is required')
    groups = []
    target_vertices = cmds.filterExpand(raw_targets, selectionMask=31, expand=True) or []
    if target_vertices:
        target_vertices = cmds.ls(target_vertices, flatten=True, long=True) or []
        by_mesh = {}
        for vertex in target_vertices:
            by_mesh.setdefault(vertex.split('.', 1)[0], []).append(vertex)
        groups.extend(sorted(by_mesh.items()))
    else:
        for target in raw_targets:
            target_mesh = _mesh_transform(target)
            vertices = cmds.ls(target_mesh + '.vtx[*]', flatten=True, long=True) or []
            groups.append((target_mesh, vertices))

    previous_selection = cmds.ls(selection=True, long=True) or []
    results = []
    try:
        for target_mesh, vertices in groups:
            target_skin = bind_like_source(source_mesh, target_mesh)
            if not target_skin:
                raise RuntimeError('Could not create target skinCluster: %s' % target_mesh)
            transfer_mode = _copy_selected_skin_weights(source_skin, target_skin, source_vertices, vertices, surface_association)
            results.append({'target_mesh': target_mesh, 'skin_cluster': target_skin, 'vertex_count': len(vertices), 'transfer_mode': transfer_mode})
    finally:
        if previous_selection:
            cmds.select(previous_selection, replace=True)
        else:
            cmds.select(clear=True)
    return results


def capture_proxy_snapshot_from_selection():
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if not selection:
        raise RuntimeError('Select a skinned proxy mesh or vertices to copy')
    return capture_proxy_snapshot(selection)


def paste_proxy_snapshot_to_selection(snapshot, surface_association='closestPoint'):
    selection = cmds.ls(selection=True, flatten=True, long=True) or []
    if not selection:
        raise RuntimeError('Select one or more target meshes or vertices to paste proxy skin')
    return paste_proxy_snapshot(snapshot, selection, surface_association=surface_association)


def create_proxy(faces, name=None, copy_skin_weights=True):
    """Create a proxy mesh from explicit faces and optionally transfer skin weights."""
    source_mesh, faces = _face_components(faces)
    proxy = extract_faces(faces, name=name)
    target_skin = copy_skin(source_mesh, proxy) if copy_skin_weights else None
    return {'source_mesh': source_mesh, 'proxy_mesh': proxy, 'skin_cluster': target_skin}


def create_mirrored_proxy(faces, axis='x', name=None, copy_skin_weights=True):
    """Extract explicit faces, mirror them across the world axis, then transfer source skin."""
    source_mesh, faces = _face_components(faces)
    axis_index = _axis_index(axis)
    direction = _region_axis_direction(faces, axis)
    proxy = extract_faces(faces, name=name)
    cmds.polyMirrorFace(
        proxy,
        cutMesh=1,
        axis=axis_index,
        axisDirection=direction,
        mergeMode=0,
        mergeThresholdType=0,
    )
    cmds.delete(proxy, constructionHistory=True)
    target_skin = copy_skin(source_mesh, proxy, surface_association='closestComponent') if copy_skin_weights else None
    return {
        'source_mesh': source_mesh,
        'proxy_mesh': proxy,
        'skin_cluster': target_skin,
        'axis': str(axis).lower(),
        'axis_direction': direction,
    }


def create_proxy_from_selection(name=None, copy_skin_weights=True):
    faces = cmds.filterExpand(cmds.ls(selection=True, flatten=True, long=True) or [], selectionMask=34) or []
    if not faces:
        raise RuntimeError('Select one or more polygon faces from a single mesh')
    return create_proxy(faces, name=name, copy_skin_weights=copy_skin_weights)


def create_mirrored_proxy_from_selection(axis='x', name=None, copy_skin_weights=True):
    faces = cmds.filterExpand(cmds.ls(selection=True, flatten=True, long=True) or [], selectionMask=34) or []
    if not faces:
        raise RuntimeError('Select one or more polygon faces from a single mesh')
    return create_mirrored_proxy(faces, axis=axis, name=name, copy_skin_weights=copy_skin_weights)
