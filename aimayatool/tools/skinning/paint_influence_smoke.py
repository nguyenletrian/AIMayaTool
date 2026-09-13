from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import paint_influence

_MARKER = 'AIBRIDGE_UI_SMOKE_OK:SKINNING_PAINT_INFLUENCE_SMOKE_OK'


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def run_paint_influence_smoke():
    cmds.file(new=True, force=True)

    joint_a = cmds.joint(name='paintInfA', position=(-1.0, 0.0, 0.0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='paintInfB', position=(1.0, 0.0, 0.0))
    mesh = cmds.polyPlane(name='paintInfluenceMesh', width=2.0, height=2.0, subdivisionsX=1, subdivisionsY=1)[0]
    cmds.skinCluster([joint_a, joint_b], mesh, toSelectedBones=True, normalizeWeights=1)

    cmds.setAttr(joint_a + '.liw', False)
    cmds.setAttr(joint_b + '.liw', True)
    before = paint_influence.lock_state(mesh)
    _assert(before[joint_a] is False and before[joint_b] is True, 'Initial lock state mismatch')

    snapshot = paint_influence.isolate(mesh, joint_b)
    isolated = paint_influence.lock_state(mesh)
    _assert(snapshot == before, 'Isolate did not return original lock state')
    _assert(isolated[joint_a] is True and isolated[joint_b] is False, 'Influence isolation mismatch')

    restored = paint_influence.restore(snapshot)
    after = paint_influence.lock_state(mesh)
    _assert(after == before, 'Lock state restore mismatch')
    _assert(restored == before, 'Restore result mismatch')

    all_locked = paint_influence.set_all_locked(mesh, True)
    _assert(all(all_locked.values()), 'set_all_locked(True) failed')
    all_unlocked = paint_influence.set_all_locked(mesh, False)
    _assert(not any(all_unlocked.values()), 'set_all_locked(False) failed')

    try:
        paint_influence.isolate(mesh, 'notBoundJoint')
    except ValueError:
        pass
    else:
        raise AssertionError('Unbound influence must be rejected')

    print(_MARKER)
    return _MARKER
