from __future__ import absolute_import

from contextlib import contextmanager


def _cmds():
    import maya.cmds as cmds
    return cmds


@contextmanager
def undo_chunk(name='AIMayaTool'):
    """Group host mutations into one Maya undo step and always close the chunk."""
    cmds = _cmds()
    cmds.undoInfo(openChunk=True, chunkName=name)
    try:
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


def run_undoable(callback, name='AIMayaTool'):
    if not callable(callback):
        raise TypeError('callback must be callable')
    with undo_chunk(name):
        return callback()
