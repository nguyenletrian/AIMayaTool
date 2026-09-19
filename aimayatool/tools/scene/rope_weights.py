from __future__ import absolute_import

def normalize_pairs(objects, destinations):
    def names(value):
        if isinstance(value, str): value=value.splitlines()
        return [str(x).strip() for x in (value or []) if str(x).strip()]
    objects,destinations=names(objects),names(destinations)
    if not objects or len(objects)!=len(destinations): raise ValueError("Objects and destinations must be non-empty and have equal cardinality.")
    return list(zip(objects,destinations))

def weights(mode, count, driver, offset=0):
    count=int(count); effective=float(driver)+int(offset)
    if count<=0: raise ValueError("count must be positive")
    if mode=="roll": active=float(count)-effective
    elif mode=="straight": active=effective
    else: raise ValueError("mode must be roll or straight")
    denominator=active+1.0
    if denominator==0.0: raise ValueError("weight denominator is zero")
    result=[]
    for i in range(1,count+1):
        enabled=1.0 if active>=i else 0.0
        result.append({"start":((active-(i-1))/denominator)*enabled,"end":(i/denominator)*enabled,"destination":1.0-enabled,"orient_reference":enabled,"orient_destination":1.0-enabled})
    return result


def rope_weights_managed_maya_smoke(mode="roll"):
    """Managed Maya smoke for deterministic RopeRoll/RopeStraight host weight wiring."""
    try:
        from maya import cmds
    except ImportError:
        raise RuntimeError("Maya runtime is required")
    if mode not in ("roll", "straight"):
        raise ValueError("mode must be roll or straight")
    prefix="AIBridgeRopeWeights_"+mode
    driver=cmds.createNode("transform", name=prefix+"_Driver")
    cmds.addAttr(driver, longName="value", attributeType="double", keyable=True)
    objects=[]; destinations=[]; constraints=[]
    for i in range(3):
        start=cmds.createNode("transform", name=prefix+"_Start_%02d"%(i+1))
        end=cmds.createNode("transform", name=prefix+"_End_%02d"%(i+1))
        dest=cmds.createNode("transform", name=prefix+"_Destination_%02d"%(i+1))
        driven=cmds.createNode("transform", name=prefix+"_Driven_%02d"%(i+1))
        constraint=cmds.pointConstraint(start,end,dest,driven,maintainOffset=False)[0]
        objects.append((start,end)); destinations.append(dest); constraints.append(constraint)
    sample_driver=1.0 if mode=="straight" else 2.0
    expected=weights(mode,3,sample_driver,0)
    for i,constraint in enumerate(constraints):
        aliases=cmds.pointConstraint(constraint,query=True,weightAliasList=True) or []
        if len(aliases)!=3: raise RuntimeError("Expected three pointConstraint weights")
        for alias,value in zip(aliases,(expected[i]["start"],expected[i]["end"],expected[i]["destination"])):
            cmds.setAttr(constraint+"."+alias,value)
        actual=[cmds.getAttr(constraint+"."+alias) for alias in aliases]
        wanted=[expected[i]["start"],expected[i]["end"],expected[i]["destination"]]
        if any(abs(a-b)>1e-6 for a,b in zip(actual,wanted)): raise RuntimeError("Constraint weight mismatch")
    return {"ok":True,"mode":mode,"constraint_count":len(constraints),"weights":expected}


def rope_straight_managed_maya_smoke():
    return rope_weights_managed_maya_smoke("straight")


def normalize_rope_runtime(data, mode):
    data=dict(data or {})
    pairs=normalize_pairs(data.get("objsRun"),data.get("destinations"))
    if mode not in ("roll","straight"): raise ValueError("mode must be roll or straight")
    result={"mode":mode,"objStart":str(data.get("objStart","")).strip(),"objEnd":str(data.get("objEnd","")).strip(),
            "pairs":pairs,"attrContent":str(data.get("attrContent","")).strip(),"attr":str(data.get("attr","")).strip(),
            "constraintContent":str(data.get("constraintContent","")).strip(),"orientReference":str(data.get("orientReference","")).strip(),
            "offset":int(data.get("offset",0))}
    for key in ("objStart","objEnd","attrContent","attr","orientReference"):
        if not result[key]: raise ValueError(key+" is required")
    return result

def apply_rope_runtime(data, mode):
    from maya import cmds
    plan=normalize_rope_runtime(data,mode); count=len(plan["pairs"])
    names=[plan["objStart"],plan["objEnd"],plan["attrContent"],plan["orientReference"]]
    names += [x for pair in plan["pairs"] for x in pair]
    missing=[x for x in names if not cmds.objExists(x)]
    if missing: raise ValueError("Missing rope objects: "+", ".join(missing))
    if plan["constraintContent"] and not cmds.objExists(plan["constraintContent"]): raise ValueError("Missing constraintContent: "+plan["constraintContent"])
    max_value=max(count-plan["offset"],0)
    if not cmds.attributeQuery(plan["attr"],node=plan["attrContent"],exists=True):
        cmds.addAttr(plan["attrContent"],longName=plan["attr"],attributeType="long",minValue=0,maxValue=max_value,defaultValue=0,keyable=True)
    driver=plan["attrContent"]+"."+plan["attr"]; created=[]
    for i,(obj,dest) in enumerate(plan["pairs"],1):
        point=cmds.pointConstraint(plan["objStart"],plan["objEnd"],dest,obj,maintainOffset=False)[0]
        orient=cmds.orientConstraint(plan["orientReference"],dest,obj,maintainOffset=False)[0]
        if plan["constraintContent"]: cmds.parent(point,orient,plan["constraintContent"])
        created.append({"object":obj,"destination":dest,"pointConstraint":point,"orientConstraint":orient,"index":i})
    def update(*_):
        values=weights(mode,count,cmds.getAttr(driver),plan["offset"])
        for entry,value in zip(created,values):
            p=entry["pointConstraint"]; pa=cmds.pointConstraint(p,query=True,weightAliasList=True) or []
            o=entry["orientConstraint"]; oa=cmds.orientConstraint(o,query=True,weightAliasList=True) or []
            for alias,v in zip(pa,(value["start"],value["end"],value["destination"])): cmds.setAttr(p+"."+alias,v)
            for alias,v in zip(oa,(value["orient_reference"],value["orient_destination"])): cmds.setAttr(o+"."+alias,v)
        return values
    update()
    return {"plan":plan,"driver":driver,"constraints":created,"update":update}
