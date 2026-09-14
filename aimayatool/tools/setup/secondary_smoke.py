from __future__ import absolute_import
import importlib
import maya.cmds as cmds
from . import secondary as secondary_module

def _secondary(): return importlib.reload(secondary_module)
def _transform(name,x):
    node=cmds.createNode("transform",name=name); cmds.setAttr(node+".translateX",float(x)); return node

def run_setup_fold_rig_smoke():
    secondary=_secondary(); cmds.file(new=True,force=True); driver=cmds.createNode("transform",name="foldSettings"); end=_transform("foldEnd",0); dst1=_transform("foldDst1",10); dst2=_transform("foldDst2",20); obj1=_transform("foldObj1",-5); obj2=_transform("foldObj2",-10); result=secondary.create_fold_rig([obj1,obj2],end,[dst1,dst2],driver+".fold")
    for value, expected in ((0,(0,0)),(1,(0,10)),(2,(10,20))):
        cmds.setAttr(driver+".fold",value); cmds.dgdirty(allPlugs=True)
        if abs(cmds.getAttr(obj1+".translateX")-expected[0])>1e-4 or abs(cmds.getAttr(obj2+".translateX")-expected[1])>1e-4: raise RuntimeError("Fold state mismatch at driver={0}.".format(value))
    return "SETUP_FOLD_RIG_SMOKE_OK:3"

def run_setup_rope_straight_smoke():
    secondary=_secondary(); cmds.file(new=True,force=True); driver=cmds.createNode("transform",name="ropeSettings"); start=_transform("ropeStart",0); end=_transform("ropeEnd",12); orient_ref=cmds.createNode("transform",name="ropeOrientRef"); dst1=_transform("ropeDst1",2); dst2=_transform("ropeDst2",9); obj1=_transform("ropeObj1",-5); obj2=_transform("ropeObj2",-10); result=secondary.create_rope_straight([obj1,obj2],start,end,[dst1,dst2],orient_ref,driver+".rope")
    if len(result["point_constraints"])!=2 or len(result["orient_constraints"])!=2: raise RuntimeError("RopeStraight nodes missing.")
    for value,expected in ((0,(2,9)),(1,(6,9)),(2,(4,8))):
        cmds.setAttr(driver+".rope",value); cmds.dgdirty(allPlugs=True)
        if abs(cmds.getAttr(obj1+".translateX")-expected[0])>1e-4 or abs(cmds.getAttr(obj2+".translateX")-expected[1])>1e-4: raise RuntimeError("RopeStraight state mismatch at driver={0}.".format(value))
    return "SETUP_ROPE_STRAIGHT_SMOKE_OK:3"

def run_setup_rope_roll_smoke():
    secondary=_secondary(); cmds.file(new=True,force=True); driver=cmds.createNode("transform",name="rollSettings"); start=_transform("rollStart",0); end=_transform("rollEnd",12); orient_ref=cmds.createNode("transform",name="rollOrientRef"); dst1=_transform("rollDst1",2); dst2=_transform("rollDst2",9); obj1=_transform("rollObj1",-5); obj2=_transform("rollObj2",-10); result=secondary.create_rope_roll([obj1,obj2],start,end,[dst1,dst2],orient_ref,driver+".roll")
    if len(result["point_constraints"])!=2 or len(result["orient_constraints"])!=2: raise RuntimeError("RopeRoll nodes missing.")
    for value,expected in ((0,(4,8)),(1,(6,9)),(2,(2,9))):
        cmds.setAttr(driver+".roll",value); cmds.dgdirty(allPlugs=True)
        if abs(cmds.getAttr(obj1+".translateX")-expected[0])>1e-4 or abs(cmds.getAttr(obj2+".translateX")-expected[1])>1e-4: raise RuntimeError("RopeRoll state mismatch at driver={0}.".format(value))
    return "SETUP_ROPE_ROLL_SMOKE_OK:3"

def run_setup_spline_ik_chain_smoke():
    secondary=_secondary(); cmds.file(new=True,force=True); refs=[]
    for name,pos in (("splineRef1",(0,0,0)),("splineRef2",(4,2,0)),("splineRef3",(8,0,0))):
        node=cmds.createNode("transform",name=name); cmds.xform(node,worldSpace=True,translation=pos); refs.append(node)
    result=secondary.create_spline_ik_chain(refs,name_prefix="splineTest")
    for node in list(result["joints"])+[result["curve"],result["handle"],result["effector"]]:
        if not node or not cmds.objExists(node): raise RuntimeError("Spline IK node missing: {0}".format(node))
    if cmds.nodeType(result["handle"])!="ikHandle": raise RuntimeError("Spline IK handle type mismatch.")
    return "SETUP_SPLINE_IK_CHAIN_SMOKE_OK:3"
