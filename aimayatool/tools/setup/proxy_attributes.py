from __future__ import absolute_import


def create_proxy_attribute(source_plug,target_node,attribute=None,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    source_plug=str(source_plug or "").strip(); target_node=str(target_node or "").strip()
    if not source_plug or not cmds.objExists(source_plug): raise ValueError("Proxy source plug does not exist: {0}".format(source_plug))
    if not target_node or not cmds.objExists(target_node): raise ValueError("Proxy target node does not exist: {0}".format(target_node))
    attr=str(attribute or source_plug.rsplit(".",1)[-1]).strip(); target_plug=target_node+"."+attr
    if cmds.objExists(target_plug): raise ValueError("Proxy target attribute already exists: {0}".format(target_plug))
    cmds.addAttr(target_node,longName=attr,proxy=source_plug)
    return target_plug


def connect_visibility(source_plug,target_node,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    target_plug=str(target_node or "").strip()+".visibility"
    if not cmds.objExists(source_plug): raise ValueError("Visibility source plug does not exist: {0}".format(source_plug))
    if not cmds.objExists(target_plug): raise ValueError("Visibility target plug does not exist: {0}".format(target_plug))
    incoming=cmds.listConnections(target_plug,source=True,destination=False,plugs=True) or []
    if incoming: raise ValueError("Visibility target already has an incoming connection: {0}".format(target_plug))
    cmds.connectAttr(source_plug,target_plug,force=False)
    return target_plug
