from __future__ import absolute_import


def run_joint_regions_smoke():
    import importlib
    import maya.cmds as cmds
    from aimayatool.tools.skinning import joint_regions
    importlib.reload(joint_regions)
    cmds.file(new=True, force=True)
    joints = []
    for name, position in [('AIMayaToolJointA', (1, 0, 0)), ('AIMayaToolJointB', (0, 1, 0)), ('AIMayaToolJointC', (-1, 0, 0)), ('AIMayaToolJointD', (0, -1, 0))]:
        cmds.select(clear=True)
        joints.append(cmds.joint(name=name, position=position))
    ordered = joint_regions.sort_circular_joints(joints)
    closest = joint_regions.closest_joints(joints[0], joints, count=2)
    if set(ordered) != set(joints) or len(ordered) != 4:
        raise RuntimeError('Circular joint ordering failed')
    if len(closest) != 2 or any(item[0] == joints[0] for item in closest):
        raise RuntimeError('Closest-joint selection failed')
    indices = joint_regions.indices_within_radius([(0, 0, 0), (1, 0, 0), (2, 0, 0)], (0, 0, 0), 1.0)
    if indices != [0, 1]:
        raise RuntimeError('Radius selection failed')
    return 'SKINNING_JOINT_REGIONS_SMOKE_OK'
