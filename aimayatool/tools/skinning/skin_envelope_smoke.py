from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import skin_envelope


_TOLERANCE = 1e-6


def _close(left, right):
    return abs(float(left) - float(right)) <= _TOLERANCE


def run_skin_envelope_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolEnvelopeMesh', subdivisionsX=1, subdivisionsY=1)[0]
    joint = cmds.joint(name='AIMayaToolEnvelopeJoint', position=(0, 0, 0))
    cluster = cmds.skinCluster(joint, mesh, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolEnvelopeSkinCluster')[0]

    if not _close(skin_envelope.value(mesh), 1.0):
        raise RuntimeError('initial envelope mismatch')
    if not _close(skin_envelope.disable(mesh), 0.0):
        raise RuntimeError('disable failed')
    if not _close(skin_envelope.toggle(mesh), 1.0):
        raise RuntimeError('toggle enable failed')

    cmds.setAttr(cluster + '.envelope', 0.35)
    snapshot = skin_envelope.snapshot([mesh])
    if set(snapshot) != {cluster} or not _close(snapshot.get(cluster, -1.0), 0.35):
        raise RuntimeError('snapshot mismatch: %s' % snapshot)
    skin_envelope.enable(mesh)
    restored = skin_envelope.restore(snapshot)
    if not _close(restored.get(cluster, -1.0), 0.35):
        raise RuntimeError('restore mismatch: %s' % restored)

    try:
        skin_envelope.value(cmds.polyCube(name='AIMayaToolUnskinnedMesh')[0])
    except RuntimeError:
        pass
    else:
        raise RuntimeError('unskinned mesh should be rejected')

    return 'SKINNING_SKIN_ENVELOPE_SMOKE_OK'
