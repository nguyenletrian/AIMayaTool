from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import topology


def run_topology_smoke():
    cmds.file(new=True, force=True)
    importlib.invalidate_caches()
    importlib.reload(topology)
    mesh = cmds.polyPlane(name='AIMayaToolTopologyMesh', subdivisionsX=1, subdivisionsY=1)[0]
    edges = cmds.ls(mesh + '.e[*]', flatten=True) or []
    if len(edges) != 4:
        raise RuntimeError('unexpected plane edge count: %s' % edges)
    vertices = topology.vertices_from_edges(mesh, edges)
    if len(vertices) != 4:
        raise RuntimeError('edge-to-vertex conversion failed: %s' % vertices)
    if not topology.is_edge_loop_closed(mesh, edges):
        raise RuntimeError('plane perimeter was not detected as closed')
    if topology.is_edge_loop_closed(mesh, edges[:2]):
        raise RuntimeError('open edge subset was incorrectly detected as closed')
    return 'SKINNING_TOPOLOGY_SMOKE_OK'
