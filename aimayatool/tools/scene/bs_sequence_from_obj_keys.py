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
