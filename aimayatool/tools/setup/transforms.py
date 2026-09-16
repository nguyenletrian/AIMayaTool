"""Reusable transform helpers for setup workflows."""
from __future__ import absolute_import


def _cmds(): import maya.cmds as cmds; return cmds

def _short_name(node): return str(node).rsplit("|",1)[-1]
def _long_name(cmds,node):
    matches=cmds.ls(node,long=True) or []
    return matches[0] if matches else node

def _require_node(cmds,node,label):
    if not node or not cmds.objExists(node): raise ValueError("{0} does not exist: {1}".format(label,node))


def world_matrix(node):
    cmds=_cmds(); _require_node(cmds,node,"Node"); return tuple(cmds.xform(node,query=True,worldSpace=True,matrix=True))

def match_world_transform(node,reference,translate=True,rotate=True,scale=True):
    cmds=_cmds(); _require_node(cmds,node,"Node"); _require_node(cmds,reference,"Reference")
    cmds.matchTransform(node,reference,position=bool(translate),rotation=bool(rotate),scale=bool(scale)); return node

def freeze_transform(node,translate=False,rotate=True,scale=True):
    cmds=_cmds(); _require_node(cmds,node,"Node"); cmds.makeIdentity(node,apply=True,translate=bool(translate),rotate=bool(rotate),scale=bool(scale),normal=False); return node

def reset_transform(node,translate=True,rotate=True,scale=True):
    cmds=_cmds(); _require_node(cmds,node,"Node")
    if translate:
        for axis in "XYZ": cmds.setAttr(node+".translate"+axis,0)
    if rotate:
        for axis in "XYZ": cmds.setAttr(node+".rotate"+axis,0)
    if scale:
        for axis in "XYZ": cmds.setAttr(node+".scale"+axis,1)
    return node

def hierarchy_between(begin,end,node_type=None):
    cmds=_cmds(); _require_node(cmds,begin,"Hierarchy begin"); _require_node(cmds,end,"Hierarchy end")
    begin=_long_name(cmds,begin); current=_long_name(cmds,end); chain=[current]
    while current!=begin:
        parents=cmds.listRelatives(current,parent=True,fullPath=True,type=node_type) or []
        if not parents: raise ValueError("End is not below begin in the requested hierarchy.")
        current=parents[0]; chain.append(current)
    return tuple(reversed(chain))
def _intermediate_joint_names(source_chain,name_prefix=None):
    return tuple("{0}{1}".format(name_prefix or "",_short_name(node)) for node in source_chain[1:-1])
def match_joint_chain(source_begin,source_end,destination_begin,destination_end,name_prefix=None):
    cmds=_cmds(); source_chain=hierarchy_between(source_begin,source_end,node_type="joint"); destination_chain=hierarchy_between(destination_begin,destination_end,node_type="joint"); destination_begin=destination_chain[0]; destination_end=destination_chain[-1]
    match_world_transform(destination_begin,source_chain[0],translate=True,rotate=False,scale=False); match_world_transform(destination_end,source_chain[-1],translate=True,rotate=False,scale=False)
    if len(destination_chain)>2:
        destination_end=cmds.parent(destination_end,destination_begin,absolute=True)[0]; cmds.delete(destination_chain[1]); destination_begin=_long_name(cmds,destination_begin); destination_end=_long_name(cmds,destination_end)
    mappings=[(destination_begin,source_chain[0])]; parent_joint=destination_begin; names=_intermediate_joint_names(source_chain,name_prefix=name_prefix)
    for source_joint,joint_name in zip(source_chain[1:-1],names):
        joint=cmds.createNode("joint",name=joint_name); cmds.matchTransform(joint,source_joint,position=True,rotation=False,scale=False); cmds.matchTransform(joint,destination_begin,position=False,rotation=True,scale=False); joint=cmds.parent(joint,parent_joint,absolute=True)[0]; parent_joint=_long_name(cmds,joint); mappings.append((parent_joint,source_joint))
    if source_chain[1:-1]: destination_end=cmds.parent(destination_end,parent_joint,absolute=True)[0]
    destination_end=_long_name(cmds,destination_end); match_world_transform(destination_end,source_chain[-1],translate=True,rotate=False,scale=False); mappings.append((destination_end,source_chain[-1])); return tuple(mappings)
def create_joint_at_reference(reference,name=None,match_rotation=True):
    cmds=_cmds(); _require_node(cmds,reference,"Joint reference"); joint_name=name or (_short_name(reference)+"_JNT"); cmds.select(clear=True); joint=cmds.createNode("joint",name=joint_name); cmds.matchTransform(joint,reference,position=True,rotation=bool(match_rotation),scale=False); return joint
def create_joints_at_references(references,suffix="_JNT",match_rotation=True):
    cmds=_cmds(); references=list(references or [])
    if not references: raise ValueError("At least one joint reference is required.")
    for reference in references: _require_node(cmds,reference,"Joint reference")
    return tuple(create_joint_at_reference(reference,name=_short_name(reference)+suffix,match_rotation=match_rotation) for reference in references)
def create_joint_hierarchy_from_transforms(root,suffix="_JNT",name_prefix=None,match_rotation=True):
    cmds=_cmds(); _require_node(cmds,root,"Hierarchy root"); root=_long_name(cmds,root); descendants=cmds.listRelatives(root,allDescendents=True,fullPath=True,type="transform") or []; sources=[root]+list(reversed(descendants)); source_set=set(sources); mapping={}; created=[]
    for source in sources:
        joint=create_joint_at_reference(source,name="{0}{1}{2}".format(name_prefix or "",_short_name(source),suffix),match_rotation=match_rotation); parents=cmds.listRelatives(source,parent=True,fullPath=True) or []; parent_source=parents[0] if parents and parents[0] in source_set else None
        if parent_source: joint=cmds.parent(joint,mapping[parent_source],absolute=True)[0]
        mapping[source]=joint; created.append(joint)
    return {"root":root,"sources":tuple(sources),"joints":tuple(created),"mapping":mapping}


def insert_offset_group(node,name=None,suffix="_fixOffset"):
    """Insert a matched transform directly above a node and preserve its exact world matrix."""
    cmds=_cmds(); _require_node(cmds,node,"Offset node"); node=_long_name(cmds,node); before=tuple(cmds.xform(node,query=True,worldSpace=True,matrix=True)); parents=cmds.listRelatives(node,parent=True,fullPath=True) or []; parent=parents[0] if parents else None; group_name=name or (_short_name(node)+suffix)
    group=cmds.createNode("transform",name=group_name)
    if parent: group=cmds.parent(group,parent,absolute=True)[0]
    cmds.xform(group,worldSpace=True,matrix=before); node=cmds.parent(node,group,absolute=True)[0]; cmds.xform(node,worldSpace=True,matrix=before)
    return {"node":node,"group":group,"parent":parent}

def remove_offset_group(group):
    """Remove an explicit offset group and reparent its children while preserving world pose."""
    cmds=_cmds(); _require_node(cmds,group,"Offset group"); group=_long_name(cmds,group); parents=cmds.listRelatives(group,parent=True,fullPath=True) or []; parent=parents[0] if parents else None; children=cmds.listRelatives(group,children=True,fullPath=True,type="transform") or []; moved=[]
    for child in children:
        moved.append(cmds.parent(child,parent,absolute=True)[0] if parent else cmds.parent(child,world=True,absolute=True)[0])
    cmds.delete(group); return {"group":group,"parent":parent,"children":tuple(moved)}
