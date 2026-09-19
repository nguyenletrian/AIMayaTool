from __future__ import absolute_import
import os

def run_script_file(path,globals_dict=None):
    script_path=os.path.abspath(str(path or "").strip())
    if not script_path: raise ValueError("path is required")
    if not os.path.isfile(script_path): raise IOError("Script file not found: {0}".format(script_path))
    namespace={"__file__":script_path,"__name__":"__aibridge_scene_single_script__"}
    if globals_dict: namespace.update(globals_dict)
    with open(script_path,"rb") as stream: source=stream.read()
    exec(compile(source,script_path,"exec"),namespace,namespace)
    return namespace

def single_script_managed_maya_smoke():
    import maya.cmds as cmds, tempfile
    fd,path=tempfile.mkstemp(suffix=".py",prefix="aibridge_single_script_"); os.close(fd)
    try:
        with open(path,"w") as stream: stream.write("import maya.cmds as cmds\\ncmds.createNode('transform', name='AIBridgeSingleScriptNode')\\nRESULT = cmds.objExists('AIBridgeSingleScriptNode')\\n")
        ns=run_script_file(path); executed=bool(ns.get("RESULT")); exists=cmds.objExists("AIBridgeSingleScriptNode")
        missing=False
        try: run_script_file(path+".missing")
        except IOError: missing=True
        smoke={"executed":executed,"exists":exists,"missing":missing}; smoke["success"]=all(smoke.values())
        if not smoke["success"]: raise AssertionError(smoke)
        print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
    finally:
        try: os.remove(path)
        except OSError: pass
