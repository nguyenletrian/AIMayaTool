from __future__ import absolute_import

def apply_transfer_attributes(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    result=[]; delete_nodes=[]
    for item in items or []:
        src=str((item or {}).get("attribute") or "").strip(); target=str((item or {}).get("target") or "").strip()
        if "." not in src: result.append({"attribute":src,"status":"skipped_invalid"}); continue
        source,attr=src.split(".",1); new_name=str((item or {}).get("newName") or attr).strip() or attr
        if not (cmds.objExists(src) and cmds.objExists(target)): result.append({"attribute":src,"target":target,"status":"skipped_missing"}); continue
        dst=target+"."+new_name
        if not cmds.attributeQuery(new_name,node=target,exists=True):
            attr_type=cmds.getAttr(src,type=True); kwargs={"ln":new_name,"k":True}
            if attr_type=="enum": kwargs.update(at="enum",en=cmds.attributeQuery(attr,node=source,listEnum=True)[0])
            else: kwargs["at"]=attr_type
            cmds.addAttr(target,**kwargs)
        cmds.setAttr(dst,cmds.getAttr(src))
        incoming=cmds.listConnections(src,s=True,d=False,p=True) or []; outgoing=cmds.listConnections(src,s=False,d=True,p=True) or []
        for plug in incoming: cmds.connectAttr(plug,dst,force=True)
        for plug in outgoing: cmds.connectAttr(dst,plug,force=True)
        if item.get("delete") and source not in delete_nodes: delete_nodes.append(source)
        result.append({"attribute":src,"target":dst,"status":"transferred","incoming":len(incoming),"outgoing":len(outgoing)})
    if delete_nodes: cmds.delete(delete_nodes)
    return result

def transfer_attribute_managed_maya_smoke():
    import maya.cmds as cmds
    src=cmds.createNode("transform",name="AIBridgeTransferSrc"); target=cmds.createNode("transform",name="AIBridgeTransferTarget"); driver=cmds.createNode("transform",name="AIBridgeTransferDriver"); driven=cmds.createNode("transform",name="AIBridgeTransferDriven")
    cmds.addAttr(src,ln="mode",at="enum",en="Off:On",k=True); cmds.setAttr(src+".mode",1); cmds.connectAttr(driver+".tx",src+".mode",force=True); cmds.connectAttr(src+".mode",driven+".ty",force=True)
    result=apply_transfer_attributes([{"attribute":src+".mode","target":target,"newName":"copiedMode","delete":False},{"attribute":"bad","target":target},{"attribute":"Missing.attr","target":target}],cmds_module=cmds)
    dst=target+".copiedMode"; attr=cmds.attributeQuery("copiedMode",node=target,exists=True); enum=cmds.attributeQuery("copiedMode",node=target,listEnum=True)[0]=="Off:On"; incoming=cmds.isConnected(driver+".tx",dst); outgoing=cmds.isConnected(dst,driven+".ty"); skips=sum(1 for x in result if x["status"].startswith("skipped"))==2
    smoke={"attr":attr,"enum":enum,"incoming":incoming,"outgoing":outgoing,"skips":skips}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
