from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import proxy_clipboard


def _total_weight(skin_cluster, component, influences):
    return sum(cmds.skinPercent(skin_cluster, component, query=True, transform=influence) for influence in influences)


def run_proxy_clipboard_smoke():
    cmds.file(new=True, force=True)
    source = cmds.polyPlane(name='AIMayaToolClipboardSource', subdivisionsX=1, subdivisionsY=1)[0]
    target = cmds.polyPlane(name='AIMayaToolClipboardTarget', subdivisionsX=1, subdivisionsY=1)[0]
    cmds.move(0.25, 0.0, 0.0, target, relative=True, worldSpace=True)

    cmds.select(clear=True)
    joint_a = cmds.joint(name='AIMayaToolClipboardJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolClipboardJointB', position=(1, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], source, normalizeWeights=1, name='AIMayaToolClipboardSourceSkin')[0]
    cmds.skinPercent(source_skin, source + '.vtx[0]', transformValue=[(joint_a, 1.0), (joint_b, 0.0)], normalize=True)
    cmds.skinPercent(source_skin, source + '.vtx[1]', transformValue=[(joint_a, 0.75), (joint_b, 0.25)], normalize=True)
    cmds.skinPercent(source_skin, source + '.vtx[2]', transformValue=[(joint_a, 0.25), (joint_b, 0.75)], normalize=True)
    cmds.skinPercent(source_skin, source + '.vtx[3]', transformValue=[(joint_a, 0.0), (joint_b, 1.0)], normalize=True)

    proxy_clipboard.clear_snapshot()
    if proxy_clipboard.has_snapshot():
        raise RuntimeError('proxy clipboard should start empty')

    cmds.select(source, replace=True)
    snapshot = proxy_clipboard.copy_from_selection()
    if not proxy_clipboard.has_snapshot() or snapshot.get('source_mesh') is None:
        raise RuntimeError('proxy clipboard snapshot was not captured')

    cmds.select(target, replace=True)
    results = proxy_clipboard.paste_to_selection()
    if len(results) != 1:
        raise RuntimeError('proxy clipboard paste did not return one target result')
    target_skin = skin.find_skin_cluster(target)
    if not target_skin:
        raise RuntimeError('proxy clipboard paste did not create target skinCluster')
    influences = skin.influences(target_skin)
    if len(influences) != 2:
        raise RuntimeError('proxy clipboard target influence count mismatch')
    target_vertices = cmds.ls(target + '.vtx[*]', flatten=True) or []
    if not target_vertices:
        raise RuntimeError('proxy clipboard target has no vertices')
    if any(abs(_total_weight(target_skin, vertex, influences) - 1.0) > 1e-5 for vertex in target_vertices):
        raise RuntimeError('proxy clipboard pasted weights are not normalized')

    proxy_clipboard.clear_snapshot()
    if proxy_clipboard.has_snapshot():
        raise RuntimeError('proxy clipboard did not clear')
    return 'SKINNING_PROXY_CLIPBOARD_SMOKE_OK'
