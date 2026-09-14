from __future__ import absolute_import

from . import naming


if naming.mirror_name("|spine_CTRL") != "|spine_CTRL":
    raise AssertionError("Root DAG path must be preserved for unmapped names.")
if naming.mirror_name("|arm_L_CTRL") != "|arm_R_CTRL":
    raise AssertionError("Root DAG path must be preserved for mirrored names.")
if naming.mirror_name("|rig_GRP|arm_L_CTRL") != "|rig_GRP|arm_R_CTRL":
    raise AssertionError("Nested DAG path must be preserved for mirrored names.")
if naming.mirror_name("char:arm_L_CTRL") != "char:arm_R_CTRL":
    raise AssertionError("Namespace context must be preserved for mirrored names.")
