from __future__ import absolute_import

TRANSFORM_ATTRS=("tx","ty","tz","rx","ry","rz","sx","sy","sz")


def normalize_keyframes(frames_by_attr):
    frames=set()
    for attr in TRANSFORM_ATTRS:
        for frame in (frames_by_attr or {}).get(attr,()) or ():
            value=float(frame)
            if value!=0.0: frames.add(value)
    return tuple(sorted(frames))


def format_frame(frame):
    value=float(frame)
    return ("{:g}".format(value))


def build_blend_weight_schedule(num_shapes):
    count=int(num_shapes)
    if count<=0: raise ValueError("BS sequence requires at least one shape.")
    segment=10.0/count; rows=[{"driver":0.0,"weights":tuple(0.0 for _ in range(count))}]
    for step in range(count):
        driver=segment*(step+1)
        if step==count-1: driver-=segment*0.5
        weights=tuple(1.0 if index==step else 0.5 if index in (step-1,step+1) else 0.0 for index in range(count))
        rows.append({"driver":driver,"weights":weights})
    rows.append({"driver":10.0,"weights":tuple(0.0 for _ in range(count))})
    return {"segment":segment,"rows":tuple(rows)}


def build_bs_sequence_plan(mesh,attr,frames):
    mesh=str(mesh or "").strip(); attr=str(attr or "").strip(); frames=tuple(float(frame) for frame in frames if float(frame)!=0.0)
    if not mesh or not attr: raise ValueError("BS sequence requires mesh and attr.")
    frames=tuple(sorted(set(frames)))
    if not frames: raise ValueError("BS sequence requires non-zero animation keyframes.")
    generated=tuple(mesh+"_Shoot_"+format_frame(frame) for frame in frames)
    return {"mesh":mesh,"attr":attr,"frames":frames,"generated_meshes":generated,"group_name":mesh+"_BSs","blendshape_name":mesh+"_"+attr+"_BS","weight_schedule":build_blend_weight_schedule(len(generated))}


def execute_bs_sequence(plan,mesh_animation,source_output,attr_holders,joint_holder,bs_parent=None,cmds_module=None,
                        sample_mesh=None,create_blendshape=None,create_attribute=None,create_proxy=None,
                        connect_visibility=None,apply_schedule=None):
    """Compose the proven BSSequence primitives as one rollback-aware Scene transaction."""
    cmds=cmds_module
    if cmds is None:
        import maya.cmds as cmds
    if sample_mesh is None:
        from aimayatool.tools.setup.mesh_sampling import sample_mesh_at_frame as sample_mesh
    if create_blendshape is None:
        from aimayatool.tools.setup.blendshapes import create_blendshape
    if create_attribute is None:
        from aimayatool.tools.setup.attributes import create_attribute
    if create_proxy is None or connect_visibility is None:
        from aimayatool.tools.setup.proxy_attributes import create_proxy_attribute,connect_visibility as _connect_visibility
        create_proxy=create_proxy or create_proxy_attribute; connect_visibility=connect_visibility or _connect_visibility
    if apply_schedule is None:
        from aimayatool.tools.setup.driven_keys import apply_driven_weight_schedule as apply_schedule

    holders=tuple(str(value).strip() for value in (attr_holders or ()) if str(value).strip())
    if not holders: raise ValueError("BS sequence requires at least one attribute holder.")
    mesh=plan["mesh"]; attr=plan["attr"]; group_name=plan["group_name"]; blend_name=plan["blendshape_name"]
    required=(mesh,mesh_animation,source_output,joint_holder)+holders
    missing=[value for value in required if not cmds.objExists(value)]
    if missing: raise ValueError("BS sequence inputs do not exist: {0}".format(", ".join(missing)))
    collisions=[value for value in tuple(plan["generated_meshes"])+(group_name,blend_name) if cmds.objExists(value)]
    attr_plugs=[holders[0]+"."+attr,joint_holder+"."+attr]+[holder+"."+attr for holder in holders[1:]]
    show_attr=attr+"ShowBS"; attr_plugs.extend(holder+"."+show_attr for holder in holders)
    collisions.extend(plug for plug in attr_plugs if cmds.objExists(plug))
    if collisions: raise ValueError("BS sequence would overwrite existing scene state: {0}".format(", ".join(collisions)))

    original_time=cmds.currentTime(query=True); created_nodes=[]; created_attrs=[]; created_connections=[]
    driver=None; original_driver=None
    try:
        generated=[]
        for frame,name in zip(plan["frames"],plan["generated_meshes"]):
            node=sample_mesh(mesh_animation,source_output,frame,name,cmds_module=cmds); generated.append(node); created_nodes.append(node)
        group=cmds.group(generated,name=group_name); created_nodes.append(group)
        if bs_parent and cmds.objExists(bs_parent): cmds.parent(group,bs_parent)
        blend=create_blendshape(generated,mesh,blend_name,cmds_module=cmds); created_nodes.append(blend)

        driver=create_attribute(holders[0],attr,attr_type="double",default=0.0,minimum=0.0,maximum=10.0,cmds_module=cmds); created_attrs.append(driver)
        original_driver=cmds.getAttr(driver)
        for holder in holders[1:]: created_attrs.append(create_proxy(driver,holder,attribute=attr,cmds_module=cmds))
        joint_plug=create_attribute(joint_holder,attr,attr_type="double",default=0.0,minimum=0.0,maximum=10.0,cmds_module=cmds); created_attrs.append(joint_plug)
        cmds.connectAttr(driver,joint_plug,force=False); created_connections.append((driver,joint_plug))
        driven=tuple(blend+".w[{0}]".format(index) for index in range(len(generated)))
        apply_schedule(driver,driven,plan["weight_schedule"],cmds_module=cmds)

        show_plug=create_attribute(holders[0],show_attr,attr_type="bool",default=False,cmds_module=cmds); created_attrs.append(show_plug)
        for holder in holders[1:]: created_attrs.append(create_proxy(show_plug,holder,attribute=show_attr,cmds_module=cmds))
        visibility=connect_visibility(show_plug,group,cmds_module=cmds); created_connections.append((show_plug,visibility))
        cmds.setAttr(driver,0.0)
        return {"generated_meshes":tuple(generated),"group":group,"blendshape":blend,"driver":driver,"show":show_plug}
    except Exception:
        for source,target in reversed(created_connections):
            try:
                if cmds.isConnected(source,target): cmds.disconnectAttr(source,target)
            except Exception: pass
        for plug in reversed(created_attrs):
            try:
                if cmds.objExists(plug): cmds.deleteAttr(plug)
            except Exception: pass
        for node in reversed(created_nodes):
            try:
                if cmds.objExists(node): cmds.delete(node)
            except Exception: pass
        raise
    finally:
        if driver and original_driver is not None and cmds.objExists(driver):
            try: cmds.setAttr(driver,original_driver)
            except Exception: pass
        cmds.currentTime(original_time,edit=True)
