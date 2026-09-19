from __future__ import absolute_import

def capture_transforms(objects,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    data={}
    for obj in objects or []:
        obj=str(obj).strip()
        if not obj or not cmds.objExists(obj): continue
        long_name=cmds.ls(obj,long=True)[0]; parent=cmds.listRelatives(long_name,parent=True,fullPath=True); joint=cmds.nodeType(long_name)=="joint"
        data[obj]={"parent":parent[0] if parent else None,"translate":cmds.xform(long_name,q=True,ws=True,t=True),"rotate":cmds.xform(long_name,q=True,ws=True,ro=True),"scale":cmds.xform(long_name,q=True,r=True,s=True),"jointOrient":cmds.getAttr(long_name+".jointOrient") if joint else None,"rotateOrder":cmds.getAttr(long_name+".rotateOrder") if joint else None,"segmentScaleCompensate":cmds.getAttr(long_name+".segmentScaleCompensate") if joint else None}
    return data

def restore_transforms(data,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    created=[]
    for obj in data or {}:
        if not cmds.objExists(obj): cmds.select(clear=True); cmds.joint(name=obj); created.append(obj)
    for obj,row in (data or {}).items():
        parent=row.get("parent")
        if parent and cmds.objExists(parent):
            try: cmds.parent(obj,parent)
            except RuntimeError: pass
    for obj,row in (data or {}).items():
        if cmds.nodeType(obj)=="joint":
            orient=row.get("jointOrient")
            if orient is not None:
                if len(orient)==1 and isinstance(orient[0],(list,tuple)): orient=orient[0]
                for axis,value in zip("XYZ",orient): cmds.setAttr(obj+".jointOrient"+axis,value)
            if row.get("rotateOrder") is not None: cmds.setAttr(obj+".rotateOrder",row["rotateOrder"])
            if row.get("segmentScaleCompensate") is not None: cmds.setAttr(obj+".segmentScaleCompensate",row["segmentScaleCompensate"])
    for obj,row in (data or {}).items(): cmds.xform(obj,ws=True,t=row["translate"],ro=row["rotate"],s=row["scale"])
    return {"created":created,"restored":list((data or {}).keys())}

def transform_backup_managed_maya_smoke():
    import maya.cmds as cmds
    root=cmds.createNode("transform",name="AIBridgeBackupRoot"); cmds.select(clear=True); joint=cmds.joint(name="AIBridgeBackupJoint"); cmds.parent(joint,root); cmds.setAttr(joint+".jointOrientX",12); cmds.setAttr(joint+".rotateOrder",2); cmds.setAttr(joint+".segmentScaleCompensate",0); cmds.xform(joint,ws=True,t=[2,3,4],ro=[5,6,7]); data=capture_transforms([joint,"MissingBackupObj"],cmds); cmds.delete(joint); result=restore_transforms(data,cmds)
    exists=cmds.objExists(joint); parent=(cmds.listRelatives(joint,parent=True) or [None])[0]==root; orient=abs(cmds.getAttr(joint+".jointOrientX")-12)<1e-6; order=cmds.getAttr(joint+".rotateOrder")==2; ssc=cmds.getAttr(joint+".segmentScaleCompensate")==0; created=joint in result["created"]
    smoke={"exists":exists,"parent":parent,"orient":orient,"rotate_order":order,"ssc":ssc,"created":created}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
