from __future__ import absolute_import


def _text(value):
    return str(value or "").strip()


def build_rename_plan(items):
    plan=[]
    for item in items or []:
        old_name=_text((item or {}).get("oldName")); new_name=_text((item or {}).get("newName"))
        if not old_name or not new_name:
            raise ValueError("Rename oldName and newName are required")
        plan.append({"old_name":old_name,"new_name":new_name})
    return plan


def apply_rename(items,cmds_module=None):
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    result=[]
    for item in build_rename_plan(items):
        old_name=item["old_name"]; new_name=item["new_name"]
        if not cmds.objExists(old_name):
            result.append({"old_name":old_name,"new_name":new_name,"status":"skipped_missing"}); continue
        actual=cmds.rename(old_name,new_name)
        result.append({"old_name":old_name,"new_name":new_name,"actual_name":actual,"status":"renamed"})
    return result


def rename_managed_maya_smoke():
    import maya.cmds as cmds
    a=cmds.createNode("transform",name="AIBridgeRenameA")
    b=cmds.createNode("transform",name="AIBridgeRenameB")
    result=apply_rename([{"oldName":a,"newName":"AIBridgeRenamedA"},{"oldName":"AIBridgeMissingRename","newName":"IgnoredName"},{"oldName":b,"newName":"AIBridgeRenamedB"}],cmds_module=cmds)
    renamed=sum(1 for x in result if x["status"]=="renamed")==2
    missing=sum(1 for x in result if x["status"]=="skipped_missing")==1
    exists=cmds.objExists("AIBridgeRenamedA") and cmds.objExists("AIBridgeRenamedB") and not cmds.objExists(a) and not cmds.objExists(b)
    invalid=False
    try: build_rename_plan([{"oldName":"","newName":"X"}])
    except ValueError: invalid=True
    smoke={"renamed":renamed,"missing":missing,"exists":bool(exists),"invalid":invalid}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
