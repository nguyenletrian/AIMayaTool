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
