from __future__ import absolute_import

import maya.cmds as cmds

from aimayatool.tools.skinning import brush_weight_smoke
from aimayatool.tools.skinning import gradient_weights_smoke
from aimayatool.tools.skinning import influence_cleanup_smoke
from aimayatool.tools.skinning import proxy_skin_smoke
from aimayatool.tools.skinning import ratio_weights_smoke
from aimayatool.tools.skinning import selection_sets_smoke
from aimayatool.tools.skinning import skin_io_parity_smoke
from aimayatool.tools.skinning import smoke
from aimayatool.tools.skinning import ui_parity_smoke


def run_skinning_regression_smoke():
    checks = [
        ('core_influences', smoke.run_smoke),
        ('max_influences', smoke.run_max_influence_smoke),
        ('copy_weights', smoke.run_copy_weights_smoke),
        ('mirror_skin', smoke.run_mirror_skin_smoke),
        ('utilities', smoke.run_skin_utilities_smoke),
        ('ratio_weights', ratio_weights_smoke.run_ratio_weights_smoke),
        ('gradient_weights', gradient_weights_smoke.run_gradient_weights_smoke),
        ('proxy_skin', proxy_skin_smoke.run_proxy_skin_smoke),
        ('selection_sets', selection_sets_smoke.run_selection_sets_smoke),
        ('brush_weight', brush_weight_smoke.run_brush_weight_smoke),
        ('skin_io', skin_io_parity_smoke.run_skin_io_parity_smoke),
        ('influence_cleanup', influence_cleanup_smoke.run_influence_cleanup_smoke),
        ('ui_parity', ui_parity_smoke.run_skinning_ui_parity_smoke),
    ]
    results = []
    for label, callback in checks:
        cmds.file(new=True, force=True)
        result = callback()
        if not result or not str(result).endswith('_OK'):
            raise RuntimeError('%s smoke did not return an OK marker: %s' % (label, result))
        results.append((label, result))
    return 'SKINNING_CONSOLIDATED_REGRESSION_OK'
