from __future__ import absolute_import


def normalize_scene_pattern_descriptor(data):
    """Normalize one ScenePattern item payload without importing Maya or legacy modules."""
    if not isinstance(data, dict):
        raise TypeError("ScenePattern descriptor must be a dictionary")
    allowed = {"parent", "child", "attrSlide", "defaultValue", "maintain"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError("Unknown ScenePattern descriptor fields: {0}".format(", ".join(unknown)))
    parent = str(data.get("parent") or "").strip()
    children = data.get("child") or ""
    if isinstance(children, str):
        children = [value.strip() for value in children.splitlines() if value.strip()]
    elif isinstance(children, (list, tuple)):
        children = [str(value).strip() for value in children if str(value).strip()]
    else:
        raise TypeError("child must be a newline string or sequence")
    attr_slide = str(data.get("attrSlide") or "Global").strip()
    if not attr_slide:
        raise ValueError("attrSlide must be non-empty")
    try:
        default_value = float(data.get("defaultValue", 0.0))
    except (TypeError, ValueError):
        raise ValueError("defaultValue must be numeric")
    maintain = data.get("maintain", True)
    if not isinstance(maintain, bool):
        raise TypeError("maintain must be boolean")
    return {
        "parent": parent,
        "children": tuple(children),
        "attr_slide": attr_slide,
        "default_value": default_value,
        "maintain": maintain,
    }


def normalize_legacy_scene_data_index(data):
    if not isinstance(data,list): raise TypeError("Legacy SceneData index must be a list")
    result=[]
    for raw in data:
        if not isinstance(raw,dict): continue
        path=raw.get("path","")
        if isinstance(path,(list,tuple)): path=path[0] if path else ""
        result.append({"id":str(raw.get("id","")).strip(),"module_name":str(raw.get("moduleName","")).strip(),
                       "name":str(raw.get("name","")).strip(),"title":str(raw.get("title","")).strip(),
                       "order":int(raw.get("order",0)),"ext":str(raw.get("ext","json")).strip().lower(),
                       "path":str(path or "").replace("\\","/")})
    return sorted(result,key=lambda x:(x["order"],x["id"],x["module_name"]))

def build_legacy_scene_data_index_plan(data):
    items=normalize_legacy_scene_data_index(data)
    return {"version":1,"items":items,"by_id":{item["id"]:item for item in items if item["id"]}}
