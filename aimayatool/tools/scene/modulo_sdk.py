from __future__ import absolute_import


def _plug(value, label):
    value=str(value).strip()
    if "." not in value: raise ValueError("%s must be node.attribute" % label)
    node,attr=value.rsplit(".",1)
    if not node or not attr: raise ValueError("%s must be node.attribute" % label)
    return node,attr


def normalize_modulo_sdk(driver, attrs_data):
    driver_node,driver_attr=_plug(driver,"driver")
    expanded={}
    for group, values in (attrs_data or {}).items():
        plugs=[x.strip() for x in str(group).splitlines() if x.strip()]
        for plug in plugs:
            _plug(plug,"target"); expanded[plug]={int(k):str(v).strip() for k,v in (values or {}).items() if str(v).strip()!=""}
    if not expanded: raise ValueError("attrs_data must contain target attributes")
    slots=sorted({k for values in expanded.values() for k in values})
    if not slots: raise ValueError("attrs_data must contain at least one modulo value")
    if min(slots)<0 or max(slots)>9: raise ValueError("modulo slots must be within 0..9")
    count=max(slots)+1
    return {"driver":driver_node+"."+driver_attr,"driver_node":driver_node,"driver_attr":driver_attr,"targets":expanded,"slots":slots,"modulo_count":count}


def modulo_slot(value, modulo_count):
    if modulo_count<=0: raise ValueError("modulo_count must be positive")
    return abs(int(value) % int(modulo_count))


def build_expression_plan(driver, attrs_data):
    data=normalize_modulo_sdk(driver,attrs_data); assignments={}
    for slot in data["slots"]:
        row=[]
        for plug,values in data["targets"].items():
            if slot in values:
                node,attr=_plug(plug,"target"); row.append({"target":node,"attr":attr,"value":values[slot],"offset":node+"_Modulo_Grp"})
        assignments[slot]=row
    data["assignments"]=assignments
    return data
