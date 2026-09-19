from __future__ import absolute_import
import re

_COMPONENT_RE = re.compile(r"^(?P<mesh>.+)\.vtx\[(?P<index>\d+)\]$")

def parse_vertex_component(component):
    value = str(component or "").strip()
    match = _COMPONENT_RE.match(value)
    if not match:
        raise ValueError("Expected vertex component mesh.vtx[index]: {0}".format(value))
    return match.group("mesh"), int(match.group("index"))

def normalize_vertex_components(values):
    if isinstance(values, str):
        values = values.splitlines()
    return [str(value).strip() for value in (values or []) if str(value).strip()]

def vertex_pair_data(sources, targets):
    sources, targets = normalize_vertex_components(sources), normalize_vertex_components(targets)
    if not sources or not targets:
        raise ValueError("Sources and targets are required.")
    if len(sources) != len(targets):
        raise ValueError("Sources and targets must have the same number of vertices.")
    source_data, target_data = [parse_vertex_component(x) for x in sources], [parse_vertex_component(x) for x in targets]
    meshes = set([x[0] for x in source_data + target_data])
    if len(meshes) != 1:
        raise ValueError("All vertex components must belong to the same mesh.")
    return {"mesh": source_data[0][0], "source_indices": [x[1] for x in source_data], "target_indices": [x[1] for x in target_data]}
