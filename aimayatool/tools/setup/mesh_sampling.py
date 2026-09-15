from __future__ import absolute_import


def sample_mesh_at_frame(mesh_animation,source_output,frame,name,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    if not cmds.objExists(mesh_animation): raise ValueError("Mesh animation does not exist: {0}".format(mesh_animation))
    if not cmds.objExists(source_output): raise ValueError("Source output does not exist: {0}".format(source_output))
    duplicate=None; destination=None; connected=False
    try:
        duplicate=cmds.duplicate(mesh_animation,name=name,inputConnections=False,upstreamNodes=False)[0]
        cmds.delete(duplicate,constructionHistory=True)
        shapes=cmds.listRelatives(duplicate,shapes=True,noIntermediate=True,fullPath=True) or []
        if not shapes: raise ValueError("Sample duplicate has no non-intermediate shape: {0}".format(duplicate))
        destination=shapes[0]+".inMesh"
        cmds.connectAttr(source_output,destination,force=True); connected=True
        cmds.currentTime(frame,edit=True)
        cmds.disconnectAttr(source_output,destination); connected=False
        cmds.delete(duplicate,constructionHistory=True)
        return duplicate
    except Exception:
        if connected and destination:
            try: cmds.disconnectAttr(source_output,destination)
            except Exception: pass
        if duplicate and cmds.objExists(duplicate):
            try: cmds.delete(duplicate)
            except Exception: pass
        raise
