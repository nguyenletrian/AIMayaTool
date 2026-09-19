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
