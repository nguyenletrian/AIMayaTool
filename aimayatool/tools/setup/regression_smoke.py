from __future__ import absolute_import

import importlib

from . import smoke as smoke_module
from . import transforms_smoke as transforms_smoke_module
from . import attributes_smoke as attributes_smoke_module
from . import constraint_smoke as constraint_smoke_module
from . import space_smoke as space_smoke_module
from . import ikfk_smoke as ikfk_smoke_module
from . import sdk_smoke as sdk_smoke_module
from . import secondary_smoke as secondary_smoke_module
from . import spline_controls_smoke as spline_controls_smoke_module
from . import spline_composition_smoke as spline_composition_smoke_module
from . import plane_projection_smoke as plane_projection_smoke_module
from . import rivet_smoke as rivet_smoke_module
from . import naming_smoke as naming_smoke_module
from . import ui_parity_smoke as ui_parity_smoke_module


def run_setup_controls_transforms_regression():
    smoke = importlib.reload(smoke_module)
    checks = (
        (smoke.run_setup_controls_smoke, "SETUP_CONTROLS_SMOKE_OK"),
        (smoke.run_setup_control_shape_catalog_smoke, "SETUP_CONTROL_SHAPE_CATALOG_SMOKE_OK:5"),
        (smoke.run_setup_transform_primitives_smoke, "SETUP_TRANSFORM_PRIMITIVES_SMOKE_OK:3"),
        (smoke.run_setup_match_joint_chain_smoke, "SETUP_MATCH_JOINT_CHAIN_SMOKE_OK:4"),
        (smoke.run_setup_control_shape_replace_smoke, "SETUP_CONTROL_SHAPE_REPLACE_SMOKE_OK:1"),
    )
    for runner, expected in checks:
        result = runner()
        if result != expected:
            raise RuntimeError("Unexpected Setup regression result: {0} != {1}".format(result, expected))
    return "SETUP_CONTROLS_TRANSFORMS_REGRESSION_OK:5"


def _run_check(module, callable_name, expected):
    module = importlib.reload(module)
    result = getattr(module, callable_name)()
    if result != expected:
        raise RuntimeError("Unexpected Setup regression result: {0} != {1}".format(result, expected))
    return result


def run_setup_complete_migration_regression():
    checks = [
        (transforms_smoke_module, "run_setup_joint_creation_smoke", "SETUP_JOINT_CREATION_SMOKE_OK:2"),
        (transforms_smoke_module, "run_setup_transform_hierarchy_smoke", "SETUP_TRANSFORM_HIERARCHY_SMOKE_OK:3"),
        (transforms_smoke_module, "run_setup_offset_group_smoke", "SETUP_OFFSET_GROUP_SMOKE_OK:1"),
        (transforms_smoke_module, "run_setup_transform_snapshot_smoke", "SETUP_TRANSFORM_SNAPSHOT_SMOKE_OK:2"),
        (transforms_smoke_module, "run_setup_match_hierarchy_smoke", "SETUP_MATCH_HIERARCHY_SMOKE_OK:3"),
        (transforms_smoke_module, "run_setup_freeze_reset_smoke", "SETUP_FREEZE_RESET_SMOKE_OK:2"),
        (attributes_smoke_module, "run_setup_attribute_copy_smoke", "SETUP_ATTRIBUTE_COPY_SMOKE_OK:2"),
        (constraint_smoke_module, "run_setup_constraint_primitives_smoke", "SETUP_CONSTRAINT_PRIMITIVES_SMOKE_OK:4"),
        (space_smoke_module, "run_setup_space_switch_smoke", "SETUP_SPACE_SWITCH_SMOKE_OK:2"),
        (ikfk_smoke_module, "run_setup_ikfk_blend_smoke", "SETUP_IKFK_BLEND_SMOKE_OK:2"),
        (ikfk_smoke_module, "run_setup_rp_ik_smoke", "SETUP_RP_IK_SMOKE_OK:1"),
        (ikfk_smoke_module, "run_setup_ikfk_switch_smoke", "SETUP_IKFK_SWITCH_SMOKE_OK:2"),
        (ikfk_smoke_module, "run_setup_ikfk_snap_smoke", "SETUP_IKFK_SNAP_SMOKE_OK:2"),
        (sdk_smoke_module, "run_setup_sdk_smoke", "SETUP_SDK_SMOKE_OK:1"),
        (sdk_smoke_module, "run_setup_sdk_proxy_attr_smoke", "SETUP_SDK_PROXY_ATTR_SMOKE_OK:1"),
        (sdk_smoke_module, "run_setup_modulo_sdk_smoke", "SETUP_MODULO_SDK_SMOKE_OK:3"),
        (secondary_smoke_module, "run_setup_fold_rig_smoke", "SETUP_FOLD_RIG_SMOKE_OK:3"),
        (secondary_smoke_module, "run_setup_rope_straight_smoke", "SETUP_ROPE_STRAIGHT_SMOKE_OK:3"),
        (secondary_smoke_module, "run_setup_rope_roll_smoke", "SETUP_ROPE_ROLL_SMOKE_OK:3"),
        (secondary_smoke_module, "run_setup_spline_ik_chain_smoke", "SETUP_SPLINE_IK_CHAIN_SMOKE_OK:3"),
        (secondary_smoke_module, "run_setup_object_on_curve_smoke", "SETUP_OBJECT_ON_CURVE_SMOKE_OK:2"),
        (secondary_smoke_module, "run_setup_joints_between_smoke", "SETUP_JOINTS_BETWEEN_SMOKE_OK:2"),
        (spline_controls_smoke_module, "run_setup_spline_controls_smoke", "SETUP_SPLINE_CONTROLS_SMOKE_OK:4"),
        (spline_composition_smoke_module, "run_setup_spline_composition_smoke", "SETUP_SPLINE_COMPOSITION_SMOKE_OK:4"),
        (plane_projection_smoke_module, "run_setup_plane_projection_smoke", "SETUP_PLANE_PROJECTION_SMOKE_OK:3"),
        (rivet_smoke_module, "run_setup_rivet_smoke", "SETUP_RIVET_SMOKE_OK:2"),
        (naming_smoke_module, "run_setup_naming_namespace_smoke", "SETUP_NAMING_NAMESPACE_SMOKE_OK:4"),
        (ui_parity_smoke_module, "run_setup_ui_core_parity_smoke", "SETUP_UI_CORE_PARITY_OK:33"),
    ]
    run_setup_controls_transforms_regression()
    for module, callable_name, expected in checks:
        _run_check(module, callable_name, expected)
    return "SETUP_COMPLETE_MIGRATION_REGRESSION_OK:{0}".format(len(checks) + 5)
