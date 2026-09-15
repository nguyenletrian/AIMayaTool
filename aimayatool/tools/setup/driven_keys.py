from __future__ import absolute_import


def apply_driven_weight_schedule(driver_plug,driven_plugs,schedule,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    driver_plug=str(driver_plug or "").strip(); driven_plugs=tuple(driven_plugs or ()); rows=tuple((schedule or {}).get("rows",()) or ())
    if not driver_plug or not cmds.objExists(driver_plug): raise ValueError("SDK driver plug does not exist: {0}".format(driver_plug))
    if not driven_plugs: raise ValueError("SDK requires driven plugs.")
    missing=[plug for plug in driven_plugs if not cmds.objExists(plug)]
    if missing: raise ValueError("SDK driven plugs do not exist: {0}".format(", ".join(missing)))
    if not rows: raise ValueError("SDK schedule has no rows.")
    original=cmds.getAttr(driver_plug)
    try:
        for row in rows:
            weights=tuple(row["weights"])
            if len(weights)!=len(driven_plugs): raise ValueError("SDK row weight count does not match driven plugs.")
            cmds.setAttr(driver_plug,float(row["driver"]))
            for plug,value in zip(driven_plugs,weights):
                cmds.setAttr(plug,float(value)); cmds.setDrivenKeyframe(plug,currentDriver=driver_plug)
    finally:
        cmds.setAttr(driver_plug,original)
    return True
