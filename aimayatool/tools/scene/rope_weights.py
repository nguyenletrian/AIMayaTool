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


def rope_weights_managed_maya_smoke(mode):
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
