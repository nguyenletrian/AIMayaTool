from __future__ import absolute_import


def _plug(value,label):
    value=str(value).strip()
    if "." not in value: raise ValueError("%s must be node.attribute" % label)
    node,attr=value.rsplit(".",1)
    if not node or not attr: raise ValueError("%s must be node.attribute" % label)
    return node,attr


def normalize_driven_key_item(item):
    driver=str((item or {}).get("driverAttr","")).strip(); _plug(driver,"driverAttr")
    listed=[x.strip() for x in str(item.get("drivenAttrs","")).splitlines() if x.strip()]
    for plug in listed: _plug(plug,"drivenAttr")
    keys=[]; seen=set()
    for raw in item.get("keyData") or []:
        dv=float(raw["driverValue"])
        if dv in seen: raise ValueError("duplicate driverValue")
        seen.add(dv); values={}
        for obj,attrs in (raw.get("drivenValues") or {}).items():
            obj=str(obj).strip()
            if not obj: raise ValueError("driven object must not be empty")
            values[obj]={str(a).strip():float(v) for a,v in attrs.items() if str(a).strip()}
        keys.append({"driverValue":dv,"drivenValues":values})
    keys.sort(key=lambda x:x["driverValue"])
    if not keys: raise ValueError("keyData must not be empty")
    objects=sorted({obj for k in keys for obj in k["drivenValues"]})
    return {"driverAttr":driver,"drivenAttrs":listed,"keyData":keys,"drivenObjects":objects,"offsets":{o:o+"_SDKGrp" for o in objects},"zeroOffsets":{o:o+"_ZeloSDKGrp" for o in objects}}


def build_driven_key_plan(items):
    return [normalize_driven_key_item(x) for x in (items or [])]
