from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from aimayatool.maya import skin
from aimayatool.tools.skinning import influences


def run_influence_cleanup_smoke():
    importlib.invalidate_caches()
    importlib.reload(influences)

    cmds.file(new=True, force=True)
    source = cmds.polyPlane(name='AIMayaToolInfluenceSyncSource', subdivisionsX=1, subdivisionsY=1)[0]
    target = cmds.polyPlane(name='AIMayaToolInfluenceSyncTarget', subdivisionsX=1, subdivisionsY=1)[0]
    joint_a = cmds.joint(name='AIMayaToolInfluenceSyncJointA', position=(-1, 0, 0))
    cmds.select(clear=True)
    joint_b = cmds.joint(name='AIMayaToolInfluenceSyncJointB', position=(0, 0, 0))
    cmds.select(clear=True)
    joint_unused = cmds.joint(name='AIMayaToolInfluenceSyncUnused', position=(1, 0, 0))

    source_skin = cmds.skinCluster([joint_a, joint_b], source, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolInfluenceSyncSourceSkin')[0]
    target_skin = cmds.skinCluster(joint_a, target, toSelectedBones=True, normalizeWeights=1, name='AIMayaToolInfluenceSyncTargetSkin')[0]
    influences.add(target, [joint_unused], weight=0.0, lock_weights=False)

    source_vertex = source + '.vtx[0]'
    target_vertex = target + '.vtx[0]'
    cmds.skinPercent(source_skin, source_vertex, transformValue=[(joint_a, 0.5), (joint_b, 0.5)], normalize=True)

    report = influences.add_missing_from_source(source, [target])
    if joint_b not in report.get(target, []) or joint_b not in skin.influences(target_skin):
        raise RuntimeError('source influence sync failed: %s' % report)

    # Keep the synced influence genuinely used while joint_unused remains
    # zero-weight across the whole target mesh.
    cmds.skinPercent(target_skin, target_vertex, transformValue=[(joint_a, 0.75), (joint_b, 0.25)], normalize=True)

    removed = influences.remove_unused(target)
    if joint_unused not in removed:
        raise RuntimeError('unused influence cleanup did not remove expected joint: %s' % removed)
    current = skin.influences(target_skin)
    if joint_unused in current or joint_a not in current or joint_b not in current:
        raise RuntimeError('unexpected influence set after cleanup: %s' % current)

    return 'SKINNING_INFLUENCE_CLEANUP_SMOKE_OK'
