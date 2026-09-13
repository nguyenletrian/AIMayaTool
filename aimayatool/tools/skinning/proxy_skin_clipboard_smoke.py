from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import proxy_skin


def _uuids(nodes):
    result = set()
    for node in nodes or []:
        values = cmds.ls(node, uuid=True) or []
        if not values:
            raise RuntimeError('could not resolve node identity: %s' % node)
        result.add(values[0])
    return result


def _weight(skin_cluster, component, influence):
    return cmds.skinPercent(skin_cluster, component, query=True, transform=influence)


def _weights(skin_cluster, component, influences):
    return tuple(_weight(skin_cluster, component, influence) for influence in influences)


def run_proxy_skin_clipboard_smoke():
    cmds.file(new=True, force=True)
    source = cmds.polyPlane(name='AIMayaToolProxyClipboardSource', width=4.0, height=1.0, subdivisionsX=3, subdivisionsY=1)[0]
    target = cmds.polyPlane(name='AIMayaToolProxyClipboardTarget', width=4.0, height=1.0, subdivisionsX=3, subdivisionsY=1)[0]
    cmds.move(0.0, 0.0, 3.0, target, absolute=True, worldSpace=True)
    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIMayaToolProxyClipboardJointA', position=(-2, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolProxyClipboardJointB', position=(2, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], source, normalizeWeights=1, name='AIMayaToolProxyClipboardSourceSkin')[0]
    source_vertices = cmds.ls(source + '.vtx[*]', flatten=True) or []
    for index, vertex in enumerate(source_vertices):
        value = 1.0 if index < len(source_vertices) // 2 else 0.0
        cmds.skinPercent(source_skin, vertex, transformValue=[(joint_a, value), (joint_b, 1.0 - value)], normalize=True)

    snapshot = proxy_skin.capture_proxy_snapshot(source)
    if snapshot['source_mesh'].split('|')[-1] != source:
        raise RuntimeError('clipboard snapshot source mesh mismatch')
    if len(snapshot['source_vertices']) != len(source_vertices):
        raise RuntimeError('clipboard snapshot did not capture full mesh vertices')
    if hasattr(proxy_skin, 'session'):
        raise RuntimeError('proxy clipboard must not use module-global session state')

    cmds.select(target)
    before_selection = cmds.ls(selection=True, long=True) or []
    results = proxy_skin.paste_proxy_snapshot(snapshot, target)
    after_selection = cmds.ls(selection=True, long=True) or []
    if before_selection != after_selection:
        raise RuntimeError('clipboard paste did not restore selection')
    if len(results) != 1:
        raise RuntimeError('clipboard paste result count mismatch')
    if results[0].get('transfer_mode') not in ('copySkinWeights:selectedComponents', 'legacy:closestSelectedVertex'):
        raise RuntimeError('clipboard paste did not report a supported transfer mode')
    target_skin = skin.find_skin_cluster(target)
    if not target_skin:
        raise RuntimeError('clipboard paste did not bind target')
    influences = [joint_a, joint_b]
    if _uuids(skin.influences(target_skin)) != _uuids(influences):
        raise RuntimeError('clipboard paste influence identity mismatch')
    target_vertices = cmds.ls(target + '.vtx[*]', flatten=True) or []
    if any(abs(sum(_weight(target_skin, vertex, joint) for joint in influences) - 1.0) > 1e-5 for vertex in target_vertices):
        raise RuntimeError('clipboard pasted weights are not normalized')

    component_target = target_vertices[:2]
    untouched_vertices = target_vertices[2:]
    untouched_before = dict((vertex, _weights(target_skin, vertex, influences)) for vertex in untouched_vertices)
    component_snapshot = proxy_skin.capture_proxy_snapshot(source_vertices[:2])
    component_results = proxy_skin.paste_proxy_snapshot(component_snapshot, component_target)
    if len(component_results) != 1 or component_results[0]['vertex_count'] != 2:
        raise RuntimeError('component clipboard paste did not stay component-scoped')
    for vertex in untouched_vertices:
        before = untouched_before[vertex]
        after = _weights(target_skin, vertex, influences)
        if any(abs(before[index] - after[index]) > 1e-6 for index in range(len(influences))):
            raise RuntimeError('component clipboard paste modified an unrelated target vertex: %s' % vertex)

    return 'SKINNING_PROXY_SKIN_CLIPBOARD_SMOKE_OK'
