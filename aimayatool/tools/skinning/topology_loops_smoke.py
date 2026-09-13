from __future__ import absolute_import


def run_topology_loops_smoke():
    import importlib
    import maya.cmds as cmds
    from aimayatool.tools.skinning import topology_axis, topology_loops
    importlib.reload(topology_axis)
    importlib.reload(topology_loops)
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolTopologyLoopMesh', width=2.0, height=2.0, subdivisionsX=2, subdivisionsY=2)[0]
    joint = cmds.joint(name='AIMayaToolTopologyLoopJoint', position=(0.0, 0.0, 0.0))
    parallel = topology_loops.joint_axis_edge_loop(mesh, joint, 4)
    perpendicular = topology_loops.joint_axis_edge_loop(mesh, joint, 4, perpendicular=True)
    if not parallel or not perpendicular:
        raise RuntimeError('Expected joint-axis edge loops')
    if not all(edge.startswith(mesh + '.e[') for edge in parallel + perpendicular):
        raise RuntimeError('Unexpected edge-loop components')
    return 'SKINNING_TOPOLOGY_LOOPS_SMOKE_OK'
