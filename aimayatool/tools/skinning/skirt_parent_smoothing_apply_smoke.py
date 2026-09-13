from __future__ import absolute_import


def run_skirt_parent_smoothing_apply_smoke():
    import maya.cmds as cmds
    from .skirt_parent_smoothing_apply import apply_smoothing_plan

    mesh = cmds.polyPlane(name='AIBridgeSkirtSmoothMesh', width=2.0, height=1.0, subdivisionsX=2, subdivisionsY=1)[0]
    source = cmds.joint(name='AIBridgeSkirtSource_JNT', position=(-1.0, 0.0, 0.0))
    cmds.select(clear=True)
    target = cmds.joint(name='AIBridgeSkirtTarget_JNT', position=(1.0, 0.0, 0.0))
    cmds.select(clear=True)
    skin = cmds.skinCluster(source, target, mesh, toSelectedBones=True, normalizeWeights=1)[0]

    vertices = ['%s.vtx[%d]' % (mesh, index) for index in range(6)]
    for vertex in vertices:
        cmds.skinPercent(skin, vertex, transformValue=[(source, 1.0), (target, 0.0)], normalize=True)

    root_far = vertices[0]
    root_near = vertices[2]
    strip_far = vertices[3]
    strip_near = vertices[5]
    plan = {
        'mesh': mesh,
        'operations': [{
            'source_joint': source,
            'target_joint': target,
            'active_joint': target,
            'influences': [source, target],
            'root_vertices': [root_far, root_near],
            'strips': {root_far: [root_far, strip_far], root_near: [root_near, strip_near]},
        }],
    }

    result = apply_smoothing_plan(skin, plan, sampler=lambda value: value)
    if len(result) != 1:
        raise RuntimeError('Expected one smoothing operation result')

    far_target = cmds.skinPercent(skin, root_far, query=True, transform=target)
    near_target = cmds.skinPercent(skin, root_near, query=True, transform=target)
    strip_far_target = cmds.skinPercent(skin, strip_far, query=True, transform=target)
    strip_near_target = cmds.skinPercent(skin, strip_near, query=True, transform=target)

    if near_target <= far_target + 0.5:
        raise RuntimeError('Expected near root target weight to exceed far root weight')
    if abs(strip_far_target - far_target) > 1e-5:
        raise RuntimeError('Far strip ratio did not match its root vertex')
    if abs(strip_near_target - near_target) > 1e-5:
        raise RuntimeError('Near strip ratio did not match its root vertex')

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_SKIRT_PARENT_SMOOTHING_APPLY_SMOKE_OK'
