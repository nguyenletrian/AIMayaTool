from __future__ import absolute_import
import os
IMAGE_EXTENSIONS={".tga",".png",".jpg",".jpeg",".tif",".tiff",".dds",".bmp",".exr",".hdr"}

def build_file_map(path):
    root_path=str(path or "").strip()
    if not root_path: raise ValueError("path is required")
    found={}
    for root,_,files in os.walk(root_path):
        for name in files:
            if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS: found[name.lower()]=os.path.join(root,name).replace("\\","/")
    return found

def replace_texture_paths(items,cmds_module=None,file_map_builder=None):
    cmds=cmds_module
    if cmds is None: import maya.cmds as cmds
    builder=file_map_builder or build_file_map; result=[]
    for item in items or []:
        file_map=builder((item or {}).get("path"))
        for node in cmds.ls(type="file") or []:
            plug=node+".fileTextureName"; value=cmds.getAttr(plug)
            if not value: continue
            old=value.replace("\\","/"); new=file_map.get(os.path.basename(old).lower())
            if not new or old==new: continue
            cmds.setAttr(plug,new,type="string"); result.append({"node":node,"old_path":old,"new_path":new,"status":"replaced"})
    return result

def replace_path_managed_maya_smoke():
    import maya.cmds as cmds
    a=cmds.shadingNode("file",asTexture=True,name="AIBridgeReplacePathA"); b=cmds.shadingNode("file",asTexture=True,name="AIBridgeReplacePathB")
    cmds.setAttr(a+".fileTextureName","C:/old/Hero_Diffuse.PNG",type="string"); cmds.setAttr(b+".fileTextureName","C:/old/Keep.exr",type="string")
    def fake(_): return {"hero_diffuse.png":"D:/textures/Hero_Diffuse.PNG"}
    result=replace_texture_paths([{"path":"unused"}],cmds_module=cmds,file_map_builder=fake)
    replaced=cmds.getAttr(a+".fileTextureName")=="D:/textures/Hero_Diffuse.PNG"; untouched=cmds.getAttr(b+".fileTextureName").replace("\\","/")=="C:/old/Keep.exr"; count=len(result)==1
    smoke={"replaced":replaced,"untouched":untouched,"count":count}; smoke["success"]=all(smoke.values())
    if not smoke["success"]: raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke)); return smoke
