from __future__ import absolute_import

import json
import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import proxy_skin


def _identity(nodes):
    result = []
    for node in nodes or []:
        long_name = (cmds.ls(node, long=True) or [node])[0]
        uuid = (cmds.ls(node, uuid=True) or [''])[0]
        result.append({'name': node, 'long': long_name, 'uuid': uuid})
    return result


def run_proxy_skin_diagnostic_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolProxyDiagSource', subdivisionsX=2, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolProxyDiagJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolProxyDiagJointB', position=(1, 0, 0))
    source_skin = cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolProxyDiagSourceSkin')[0]

    source_influences = skin.influences(source_skin)
    proxy = proxy_skin.extract_faces([mesh + '.f[0]'], name='AIMayaToolProxyDiagExtracted')
    target_skin = proxy_skin.bind_like_source(mesh, proxy)
    target_influences = skin.influences(target_skin)

    payload = {
        'source_mesh': mesh,
        'source_skin': source_skin,
        'source_influences': _identity(source_influences),
        'requested_influences': _identity([joint_a, joint_b]),
        'proxy_mesh': proxy,
        'target_skin': target_skin,
        'target_influences': _identity(target_influences),
        'source_selection': cmds.ls(selection=True, long=True) or [],
    }
    print('AIBRIDGE_PROXY_BIND_DIAGNOSTIC:' + json.dumps(payload, sort_keys=True))
    return 'SKINNING_PROXY_BIND_DIAGNOSTIC_OK'
