from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import proxy_skin


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def _uuids(nodes):
    result = set()
    for node in nodes or []:
        values = cmds.ls(node, uuid=True) or []
        if not values:
            raise RuntimeError('could not resolve node identity: %s' % node)
        result.add(values[0])
    return result


def run_proxy_skin_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolProxySource', subdivisionsX=2, subdivisionsY=1)[0]
    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIMayaToolProxyJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolProxyJointB', position=(1, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], mesh, normalizeWeights=1, name='AIMayaToolProxySourceSkin')[0]
    cmds.skinPercent(source_skin, mesh + '.vtx[0]', transformValue=[(joint_a, 1.0), (joint_b, 0.0)], normalize=True)
    cmds.skinPercent(source_skin, mesh + '.vtx[1]', transformValue=[(joint_a, 0.75), (joint_b, 0.25)], normalize=True)
    cmds.skinPercent(source_skin, mesh + '.vtx[2]', transformValue=[(joint_a, 0.25), (joint_b, 0.75)], normalize=True)
    cmds.skinPercent(source_skin, mesh + '.vtx[3]', transformValue=[(joint_a, 0.0), (joint_b, 1.0)], normalize=True)

    result = proxy_skin.create_proxy([mesh + '.f[0]'], name='AIMayaToolProxyExtracted', copy_skin_weights=True)
    proxy = result['proxy_mesh']
    if not cmds.objExists(proxy):
        raise RuntimeError('proxy mesh was not created')
    if cmds.polyEvaluate(proxy, face=True) != 1:
        raise RuntimeError('proxy face extraction count mismatch')
    if [child for child in (cmds.listRelatives(proxy, children=True, fullPath=True) or []) if cmds.nodeType(child) != 'mesh']:
        raise RuntimeError('proxy copied non-mesh source child hierarchy')
    target_skin = result['skin_cluster']
    if not target_skin or skin.find_skin_cluster(proxy) != target_skin:
        raise RuntimeError('proxy skinCluster was not created')
    if _uuids(skin.influences(target_skin)) != _uuids([joint_a, joint_b]):
        raise RuntimeError('proxy influence identity set mismatch')
    proxy_vertices = cmds.ls(proxy + '.vtx[*]', flatten=True) or []
    if not proxy_vertices:
        raise RuntimeError('proxy has no vertices')
    totals = [sum(_weight(target_skin, vtx, joint) for joint in (joint_a, joint_b)) for vtx in proxy_vertices]
    if any(abs(total - 1.0) > 1e-5 for total in totals):
        raise RuntimeError('proxy weights are not normalized after transfer')

    plain = cmds.polyPlane(name='AIMayaToolProxyPlain', subdivisionsX=1, subdivisionsY=1)[0]
    plain_result = proxy_skin.create_proxy([plain + '.f[0]'], name='AIMayaToolProxyPlainExtracted', copy_skin_weights=True)
    if plain_result['skin_cluster'] is not None:
        raise RuntimeError('unskinned source should not create target skinCluster')

    return 'SKINNING_PROXY_SKIN_EXTRACTION_SMOKE_OK'
