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
    joint_b = cmds.joint(name='paintInfB', position=(0.0, 0.0, 0.0))
    joint_c = cmds.joint(name='paintInfC', position=(1.0, 0.0, 0.0))
    cmds.select(clear=True)
    mesh = cmds.polyPlane(name='paintInfluenceMesh', width=2.0, height=2.0, subdivisionsX=1, subdivisionsY=1)[0]
    skin_cluster = cmds.skinCluster([joint_a, joint_b, joint_c], mesh, toSelectedBones=True, normalizeWeights=1)[0]
    vertex = mesh + '.vtx[0]'
    cmds.skinPercent(skin_cluster, vertex, transformValue=[(joint_a, 0.7), (joint_b, 0.3), (joint_c, 0.0)], normalize=True)

    cmds.setAttr(joint_a + '.liw', False)
    cmds.setAttr(joint_b + '.liw', True)
    cmds.setAttr(joint_c + '.liw', True)
    before = paint_influence.lock_state(mesh)
    _assert(before[joint_a] is False and before[joint_b] is True and before[joint_c] is True, 'Initial lock state mismatch')

    snapshot = paint_influence.isolate(mesh, joint_b)
    isolated = paint_influence.lock_state(mesh)
    _assert(snapshot == before, 'Isolate did not return original lock state')
    _assert(isolated[joint_a] is True and isolated[joint_b] is False and isolated[joint_c] is True, 'Influence isolation mismatch')

    restored = paint_influence.restore(snapshot)
    _assert(paint_influence.lock_state(mesh) == before, 'Lock state restore mismatch')
    _assert(restored == before, 'Restore result mismatch')

    top_two = paint_influence.top_two_influences(vertex)
    _assert(top_two == [joint_a, joint_b], 'Top-two influence ordering mismatch: %s' % top_two)
    _assert(paint_influence.unlock_top_two(vertex) == [joint_a, joint_b], 'unlock_top_two result mismatch')
    state = paint_influence.lock_state(mesh)
    _assert(state[joint_a] is False and state[joint_b] is False and state[joint_c] is True, 'unlock_top_two lock state mismatch')

    child_pair = paint_influence.unlock_relative_pair(mesh, joint_b, 'child')
    _assert(child_pair == [joint_b, joint_c], 'Child pair mismatch: %s' % child_pair)
    state = paint_influence.lock_state(mesh)
    _assert(state[joint_a] is True and state[joint_b] is False and state[joint_c] is False, 'Child pair lock state mismatch')
    _assert(paint_influence.next_unlocked(mesh, joint_b) == joint_c, 'Switch to next unlocked influence mismatch')

    parent_pair = paint_influence.unlock_relative_pair(mesh, joint_b, 'parent')
    _assert(parent_pair == [joint_b, joint_a], 'Parent pair mismatch: %s' % parent_pair)
    state = paint_influence.lock_state(mesh)
    _assert(state[joint_a] is False and state[joint_b] is False and state[joint_c] is True, 'Parent pair lock state mismatch')
    _assert(paint_influence.next_unlocked(mesh, joint_a) == joint_b, 'Unlocked cycle mismatch')

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
