from __future__ import absolute_import

import importlib


def run_topology_axis_smoke():
    import maya.cmds as cmds
    from aimayatool.tools.skinning import topology_axis
    importlib.invalidate_caches()
    importlib.reload(topology_axis)
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(width=2, height=2, subdivisionsX=1, subdivisionsY=1, name='AIMayaToolTopologyAxisSmokeMesh')[0]
    joint = cmds.joint(name='AIMayaToolTopologyAxisSmokeJoint')
    parallel = topology_axis.best_edge_by_joint_axis(mesh, joint, 0, perpendicular=False)
    perpendicular = topology_axis.best_edge_by_joint_axis(mesh, joint, 0, perpendicular=True)
    if parallel is None or perpendicular is None or parallel == perpendicular:
        raise AssertionError('Expected distinct parallel/perpendicular connected edges')
    return 'SKINNING_TOPOLOGY_AXIS_SMOKE_OK'
