from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.maya.undo import undo_chunk


def run_skinning_undo_smoke():
    cmds.file(new=True, force=True)
    node = cmds.createNode('transform', name='AIMayaToolUndoProbe')
    cmds.setAttr(node + '.tx', 0.0)

    with undo_chunk('AIMayaTool Skinning Undo'):
        cmds.setAttr(node + '.tx', 5.0)
    if abs(cmds.getAttr(node + '.tx') - 5.0) > 1e-8:
        raise RuntimeError('undo chunk mutation did not apply')
    cmds.undo()
    if abs(cmds.getAttr(node + '.tx')) > 1e-8:
        raise RuntimeError('single undo did not restore grouped mutation')

    try:
        with undo_chunk('AIMayaTool Skinning Undo Failure'):
            cmds.setAttr(node + '.ty', 7.0)
            raise RuntimeError('expected smoke failure')
    except RuntimeError as exc:
        if str(exc) != 'expected smoke failure':
            raise
    cmds.undo()
    if abs(cmds.getAttr(node + '.ty')) > 1e-8:
        raise RuntimeError('failed workflow did not leave a closable undo chunk')

    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_UNDO_BOUNDARY_OK'
