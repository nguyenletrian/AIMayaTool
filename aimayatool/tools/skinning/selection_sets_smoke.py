from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import selection_sets


def _visible(node):
    return bool(cmds.getAttr(node + '.visibility'))


def run_selection_sets_smoke():
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolSetMesh', subdivisionsX=1, subdivisionsY=1)[0]
    a = cmds.polyCube(name='AIMayaToolSetA')[0]
    b = cmds.polyCube(name='AIMayaToolSetB')[0]
    c = cmds.polyCube(name='AIMayaToolSetC')[0]

    cmds.select(mesh, a, replace=True)
    set0 = selection_sets.create_from_selection()
    cmds.select(mesh, b, replace=True)
    set1 = selection_sets.create_from_selection()
    cmds.select(mesh, c, replace=True)
    set2 = selection_sets.create_from_selection()

    prefix = selection_sets.family_prefix(mesh)
    if selection_sets.family_sets(prefix) != [set0, set1, set2]:
        raise RuntimeError('family ordering mismatch')

    index, active = selection_sets.show_index(prefix, 0)
    if index != 0 or active != set0 or not _visible(a) or _visible(b) or _visible(c):
        raise RuntimeError('show_index(0) visibility mismatch')

    index, active = selection_sets.cycle(prefix, 1)
    if index != 1 or active != set1 or _visible(a) or not _visible(b) or _visible(c):
        raise RuntimeError('next cycle visibility mismatch')

    index, active = selection_sets.cycle(prefix, -1)
    if index != 0 or active != set0:
        raise RuntimeError('previous cycle mismatch')

    deleted = selection_sets.delete_family(prefix, restore_visibility=True)
    if deleted != [set0, set1, set2]:
        raise RuntimeError('delete result mismatch: %s' % deleted)
    if selection_sets.family_sets(prefix):
        raise RuntimeError('selection sets were not deleted')
    if not (_visible(a) and _visible(b) and _visible(c)):
        raise RuntimeError('delete did not restore visibility')

    return 'SKINNING_SELECTION_SETS_SMOKE_OK'
