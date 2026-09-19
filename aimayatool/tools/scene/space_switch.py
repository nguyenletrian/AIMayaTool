from __future__ import absolute_import


def _names(value, separator=None):
    if isinstance(value, str):
        value = value.split(separator) if separator else value.splitlines()
    return [str(x).strip() for x in (value or []) if str(x).strip()]


def plan_space_switch(children, parents, attr_pick="space", enum=None, attr_slide="", default_value=1.0, maintain=True):
    children, parents = _names(children), _names(parents)
    if not children: raise ValueError("children must not be empty")
    if not parents: raise ValueError("parents must not be empty")
    if len(set(children)) != len(children) or len(set(parents)) != len(parents): raise ValueError("duplicate names are ambiguous")
    attr_pick, attr_slide = str(attr_pick).strip(), str(attr_slide).strip()
    if not attr_pick: raise ValueError("attr_pick must not be empty")
    labels = _names(enum, ";") if enum else list(parents)
    if len(labels) != len(parents): raise ValueError("enum labels must match parent count")
    if len(set(labels)) != len(labels) or any(x == "Default" for x in labels): raise ValueError("enum labels must be unique and may not use Default")
    default_value = float(default_value)
    if attr_slide and not 0.0 <= default_value <= 1.0: raise ValueError("default_value must be within 0..1 when slide is enabled")
    start = 0 if maintain else 1
    options = labels if maintain else ["Default"] + labels
    targets = [{"parent": p, "label": labels[i], "pick_index": i + start} for i, p in enumerate(parents)]
    return {"children": children, "parents": parents, "attr_pick": attr_pick, "attr_slide": attr_slide or None, "default_value": default_value, "maintain": bool(maintain), "options": options, "default_pick_index": None if maintain else 0, "targets": targets, "slide_complement": "1-slide" if attr_slide else None}
