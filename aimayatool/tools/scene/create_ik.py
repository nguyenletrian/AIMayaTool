from __future__ import absolute_import

import math
from aimayatool.tools.setup.controls import create_control, create_zero_group
from aimayatool.tools.setup.ikfk import create_ikfk_blend, create_rp_ik, wire_ikfk_switch


def _cmds(): import maya.cmds as cmds; return cmds
def _om(): import maya.api.OpenMaya as om; return om
def _sub(a,b): return tuple(x-y for x,y in zip(a,b))
def _add(a,b): return tuple(x+y for x,y in zip(a,b))
def _mul(a,s): return tuple(x*s for x in a)
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _normal(v):
    length=math.sqrt(sum(x*x for x in v))
    if length<0.0001: raise ValueError("Objects are collinear.")
    return tuple(x/length for x in v)


def build_three_point_frame(positions):
    pts=tuple(tuple(float(v) for v in p) for p in positions)
    if len(pts)!=3 or any(len(p)!=3 for p in pts): raise ValueError("CreateIK requires exactly 3 XYZ positions.")
    a,b,c=pts; normal=_normal(_cross(_sub(b,a),_sub(c,b))); forwards=(_normal(_sub(b,a)),_normal(_sub(c,b)),_normal(_sub(c,b))); frames=[]
    for pos,x in zip(pts,forwards):
        z=_normal(_cross(x,normal)); y=_normal(_cross(z,x)); frames.append({"position":pos,"x":x,"y":y,"z":z})
    return {"positions":pts,"normal":normal,"frames":tuple(frames),"pole_position":_add(b,_sub(b,_mul(_add(a,c),0.5)))}


def build_create_ik_plan(objects,parent,world_parent=None,positions=None):
    objects=tuple(objects or ())
    if len(objects)!=3: raise ValueError("CreateIK requires exactly 3 objects.")
    a,b,c=objects
    plan={"objects":objects,"parent":parent,"world_parent":world_parent,"system":a+"_IKFKSystem","origin_offsets":tuple(x+"_IKFKExtraOffset" for x in objects),"joints":tuple(x+"_Jnt" for x in objects),"fk_joints":tuple(x+"_Jnt_FK" for x in objects),"ik_joints":tuple(x+"_Jnt_IK" for x in objects),"connect_groups":tuple(x+"_ConnectGroup" for x in objects),"pole_control":b+"_PoleVector","pole_offset":b+"_PoleVector_GrpOffset","ik_control":c+"_IK","ik_offset":c+"_IK_GrpOffset","fk_controls":tuple(x+"_FK" for x in objects),"fk_offsets":tuple(x+"_FKOffset" for x in objects),"switch_attribute":"SwitchIKFK","space_attribute":"Space","use_space_switch":bool(world_parent)}
    if positions is not None: plan["frame"]=build_three_point_frame(positions)
    return plan


def _require(cmds,node,label):
    if not node or not cmds.objExists(node): raise ValueError("{0} does not exist: {1}".format(label,node))
def _duplicate_chain(cmds,joints,suffix):
    duplicates=[]; parent=None
    for joint in joints:
        dup=cmds.createNode("joint",name=joint+suffix); cmds.xform(dup,worldSpace=True,matrix=cmds.xform(joint,query=True,worldSpace=True,matrix=True))
        if parent: cmds.parent(dup,parent)
        duplicates.append(dup); parent=dup
    return duplicates


def build_create_ik(objects,parent,world_parent=None):
    cmds=_cmds(); om=_om(); objects=tuple(objects or ())
    if len(objects)!=3: return {"status":"skipped_invalid_count","objects":objects}
    missing=tuple(node for node in objects if not node or not cmds.objExists(node))
    if missing: return {"status":"skipped_missing","objects":objects,"missing":missing}
    _require(cmds,parent,"Parent")
    if world_parent: _require(cmds,world_parent,"World parent")
    raw_positions=[cmds.xform(node,query=True,worldSpace=True,translation=True) for node in objects]
    try: plan=build_create_ik_plan(objects,parent,world_parent,raw_positions)
    except ValueError: return {"status":"skipped_collinear","objects":objects}
    pts=[om.MVector(p) for p in raw_positions]; a,b,c=pts
    origin_offsets=[create_zero_group(node,suffix="_IKFKExtraOffset")[0] for node in objects]
    system=cmds.createNode("transform",name=plan["system"]); cmds.xform(system,worldSpace=True,matrix=cmds.xform(parent,query=True,worldSpace=True,matrix=True)); system=cmds.parent(system,parent)[0]
    joints=[]; connect_groups=[]
    for node,frame in zip(objects,plan["frame"]["frames"]):
        x,y,z,pos=frame["x"],frame["y"],frame["z"],frame["position"]; matrix=[x[0],x[1],x[2],0,y[0],y[1],y[2],0,z[0],z[1],z[2],0,pos[0],pos[1],pos[2],1]
        joint=cmds.createNode("joint",name=node+"_Jnt"); cmds.xform(joint,worldSpace=True,matrix=matrix); joints.append(joint)
        group=cmds.createNode("transform",name=node+"_ConnectGroup"); cmds.xform(group,worldSpace=True,matrix=cmds.xform(node,query=True,worldSpace=True,matrix=True)); connect_groups.append(group)
    cmds.parent(joints[2],joints[1]); cmds.parent(joints[1],joints[0]); cmds.parent(joints[0],system); cmds.makeIdentity(joints[0],apply=True,rotate=True)
    fk_joints=_duplicate_chain(cmds,joints,"_FK"); ik_joints=_duplicate_chain(cmds,joints,"_IK")
    for group,joint in zip(connect_groups,joints): cmds.parent(group,joint)
    pole=create_control(plan["pole_control"],shape="diamond",size=2.0); pole_offset=create_zero_group(pole,suffix="_GrpOffset")[0]; pole_pos=plan["frame"]["pole_position"]; cmds.xform(pole_offset,worldSpace=True,translation=pole_pos); cmds.parent(pole_offset,system)
    ik_ctrl=create_control(plan["ik_control"],shape="box",size=2.0,match=joints[-1]); ik_offset=create_zero_group(ik_ctrl,suffix="_GrpOffset")[0]; cmds.parent(ik_offset,system)
    fk_ctrls=[]; fk_offsets=[]
    for node,joint in zip(objects,joints):
        ctrl=create_control(node+"_FK",shape="circle",size=2.0,match=joint); offset=create_zero_group(ctrl,suffix="Offset")[0]; fk_ctrls.append(ctrl); fk_offsets.append(offset)
    for index in range(len(fk_ctrls)-1): cmds.parent(fk_offsets[index+1],fk_ctrls[index])
    cmds.parent(fk_offsets[0],system)
    for ctrl,joint in zip(fk_ctrls,fk_joints): cmds.parentConstraint(ctrl,joint)
    rp=create_rp_ik(ik_joints,ik_ctrl,pole,handle_name=ik_joints[0]+"_IKHandle",orient_end=True,maintain_offset=True)
    switch_attr=ik_ctrl+".SwitchIKFK"; cmds.addAttr(ik_ctrl,longName="SwitchIKFK",attributeType="double",min=0,max=1,defaultValue=1,keyable=True)
    blend=create_ikfk_blend(joints,fk_joints,ik_joints,switch_attr,reverse_name=ik_ctrl+"_IKFK_Reverse"); visibility=wire_ikfk_switch(switch_attr,fk_offsets,[ik_offset,pole_offset],proxy_nodes=fk_ctrls+[pole],reverse_node=blend["reverse"])
    space_constraints=[]
    if world_parent:
        for ctrl,offset in ((ik_ctrl,ik_offset),(pole,pole_offset)):
            space=create_zero_group(offset,suffix=ctrl+"_IKFKSpaceSwitch")[0]; constraint=cmds.parentConstraint(parent,world_parent,space,maintainOffset=True)[0]; cmds.addAttr(ctrl,longName="Space",attributeType="enum",enumName="Local:World",keyable=True); reverse=cmds.createNode("reverse",name=ctrl+"_SpaceReverse"); cmds.connectAttr(ctrl+".Space",reverse+".inputX",force=True); weights=cmds.parentConstraint(constraint,query=True,weightAliasList=True) or []; cmds.connectAttr(reverse+".outputX",constraint+"."+weights[0],force=True); cmds.connectAttr(ctrl+".Space",constraint+"."+weights[1],force=True); space_constraints.append(constraint)
    origin_constraints=[cmds.parentConstraint(group,offset,maintainOffset=True)[0] for group,offset in zip(connect_groups,origin_offsets)]
    for node in joints+fk_joints+ik_joints+[rp["handle"]]: cmds.setAttr(node+".visibility",0)
    for node in objects:
        for shape in cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True) or []: cmds.setAttr(shape+".visibility",0)
    return {"status":"applied","system":system,"joints":tuple(joints),"fk_joints":tuple(fk_joints),"ik_joints":tuple(ik_joints),"fk_controls":tuple(fk_ctrls),"ik_control":ik_ctrl,"pole_control":pole,"ik_handle":rp["handle"],"switch_attr":switch_attr,"origin_offsets":tuple(origin_offsets),"origin_constraints":tuple(origin_constraints),"space_constraints":tuple(space_constraints),"visibility":visibility}
