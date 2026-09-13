from __future__ import absolute_import

from .skirt_parent import build_skirt_parent_plan
from .skirt_parent_transfer import apply_parent_transfers
from .skirt_parent_smoothing import build_smoothing_plan
from .skirt_parent_smoothing_apply import apply_smoothing_plan


def run_skirt_parent_workflow(mesh, skin_cluster, joint_parent, joints, root_loop, plan_builder=None, transfer_applier=None, smoothing_builder=None, smoothing_applier=None, normalize=True, **plan_kwargs):
    """Run the proven SkirtParent phases in order and return explicit evidence for each stage."""
    if not mesh:
        raise ValueError('mesh is required')
    if not skin_cluster:
        raise ValueError('skin_cluster is required')
    plan_builder = plan_builder or build_skirt_parent_plan
    transfer_applier = transfer_applier or apply_parent_transfers
    smoothing_builder = smoothing_builder or build_smoothing_plan
    smoothing_applier = smoothing_applier or apply_smoothing_plan

    plan = plan_builder(mesh, joint_parent, joints, root_loop, **plan_kwargs)
    transfers = transfer_applier(skin_cluster, plan, normalize=normalize)
    smoothing_plan = smoothing_builder(plan)
    smoothing = smoothing_applier(skin_cluster, smoothing_plan, normalize=normalize)
    return {
        'plan': plan,
        'transfers': transfers,
        'smoothing_plan': smoothing_plan,
        'smoothing': smoothing,
    }
