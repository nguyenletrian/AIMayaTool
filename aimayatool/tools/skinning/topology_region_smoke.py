from __future__ import absolute_import


def run_topology_region_smoke():
    import importlib
    import maya.cmds as cmds
    from aimayatool.tools.skinning import topology_region
    importlib.reload(topology_region)
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolTopologyRegionMesh', width=4.0, height=2.0, subdivisionsX=4, subdivisionsY=1)[0]
    loop_edges = ['%s.e[%d]' % (mesh, edge_id) for edge_id in range(cmds.polyEvaluate(mesh, edge=True))]
    source = (-1.5, 0.0, 0.0)
    target = (1.5, 0.0, 0.0)
    result = topology_region.edge_region_between_points(mesh, loop_edges, source, target)
    if result['source_edge'] is None or result['target_edge'] is None:
        raise RuntimeError('Expected nearest source/target edges')
    if not result['edges'] or not result['vertices']:
        raise RuntimeError('Expected non-empty topology region')
    return 'SKINNING_TOPOLOGY_REGION_SMOKE_OK'
