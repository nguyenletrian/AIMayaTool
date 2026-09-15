from __future__ import absolute_import


def create_blendshape(targets,destination,name,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    targets=tuple(targets or ()); destination=str(destination or "").strip(); name=str(name or "").strip()
    if not targets: raise ValueError("BlendShape requires at least one target.")
    if not destination or not cmds.objExists(destination): raise ValueError("BlendShape destination does not exist: {0}".format(destination))
    missing=[target for target in targets if not cmds.objExists(target)]
    if missing: raise ValueError("BlendShape targets do not exist: {0}".format(", ".join(missing)))
    if not name: raise ValueError("BlendShape requires a node name.")
    if cmds.objExists(name): raise ValueError("BlendShape node already exists: {0}".format(name))
    result=cmds.blendShape(*(targets+(destination,)),name=name)
    if not result: raise RuntimeError("blendShape creation returned no node.")
    return result[0]
