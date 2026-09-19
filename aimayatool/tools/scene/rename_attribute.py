from __future__ import absolute_import


def _text(value): return str(value or "").strip()


def apply_rename_attributes(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    result=[]
    for item in items or []:
        plug=_text((item or {}).get("attribute")); new_name=_text((item or {}).get("newName"))
        if not plug or "." not in plug or not new_name: raise ValueError("attribute plug and newName are required")
        if not cmds.objExists(plug): result.append({"attribute":plug,"status":"skipped_missing"}); continue
        node=plug.split(".",1)[0]
        if cmds.attributeQuery(new_name,node=node,exists=True): result.append({"attribute":plug,"status":"skipped_existing","new_name":new_name}); continue
        cmds.renameAttr(plug,new_name); new_plug=node+"."+new_name; cmds.addAttr(new_plug,e=True,nn=new_name)
        result.append({"attribute":plug,"new_plug":new_plug,"status":"renamed"})
    return result


def rename_attribute_managed_maya_smoke():
    import maya.cmds as cmds
    node=cmds.createNode("transform",name="AIBridgeRenameAttrNode"); cmds.addAttr(node,longName="oldAttr",attributeType="double"); cmds.addAttr(node,longName="existingAttr",attributeType="double")
    result=apply_rename_attributes([{"attribute":node+".oldAttr","newName":"renamedAttr"},{"attribute":node+".missingAttr","newName":"ignoredAttr"},{"attribute":node+".renamedAttr","newName":"existingAttr"}],cmds_module=cmds)
    renamed=cmds.objExists(node+".renamedAttr") and not cmds.objExists(node+".oldAttr")
    missing=sum(1 for x in result if x["status"]=="skipped_missing")==1; existing=sum(1 for x in result if x["status"]=="skipped_existing")==1
    invalid=False
    try: apply_rename_attributes([{"attribute":"bad","newName":"x"}],cmds_module=cmds)
    except ValueError: invalid=True
    smoke={"renamed":bool(renamed),"missing":missing,"existing":existing,"invalid":invalid}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
