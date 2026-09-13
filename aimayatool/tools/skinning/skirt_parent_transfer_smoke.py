from __future__ import absolute_import


def run_skirt_parent_transfer_smoke():
    import importlib
    import maya.cmds as cmds
    from aimayatool.tools.skinning import skirt_parent_transfer
    importlib.reload(skirt_parent_transfer)

    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSkirtTransferMesh', width=2.0, height=2.0, subdivisionsX=1, subdivisionsY=1)[0]
    parent = cmds.createNode('joint', name='AIMayaToolSkirtParent')
    child = cmds.createNode('joint', name='AIMayaToolSkirtChild')
    skin = cmds.skinCluster([parent, child], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolSkirtTransferSkin')[0]
    components = ['%s.vtx[%d]' % (mesh, index) for index in range(4)]
    for component in components:
        cmds.skinPercent(skin, component, transformValue=[(parent, 1.0), (child, 0.0)], normalize=True)

    plan = {
        'joint_parent': parent,
        'assignments': [
            {
                'joint': child,
                'strips': {
                    components[0]: list(components),
                    components[1]: [components[1], components[2]],
                },
            }
        ],
    }
    result = skirt_parent_transfer.apply_parent_transfers(skin, plan)
    if len(result) != 1 or len(result[0]['components']) != 4 or len(result[0]['changed']) != 4:
        raise RuntimeError('Unexpected skirt parent transfer result')
    for component in components:
        parent_weight = cmds.skinPercent(skin, component, query=True, transform=parent)
        child_weight = cmds.skinPercent(skin, component, query=True, transform=child)
        if parent_weight > 1e-6 or abs(child_weight - 1.0) > 1e-6:
            raise RuntimeError('Expected full parent-to-child transfer on %s' % component)
    return 'SKINNING_SKIRT_PARENT_TRANSFER_SMOKE_OK'
