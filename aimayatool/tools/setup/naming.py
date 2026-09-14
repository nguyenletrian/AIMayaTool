from __future__ import absolute_import

import re


_LEGACY_NAME_REPLACEMENTS = ("FBXASC046", "FBXASC045", "FBXASC032", "[", "]", ".")
_MIRROR_SWAP = {
    "L": "R", "R": "L", "l": "r", "r": "l",
    "Left": "Right", "Right": "Left", "left": "right", "right": "left", "LEFT": "RIGHT", "RIGHT": "LEFT",
    "Lf": "Rt", "Rt": "Lf", "lf": "rt", "rt": "lf", "LF": "RT", "RT": "LF",
}
_MIRROR_PATTERNS = (
    r"(?<=_)(L|R|l|r)(?=_)", r"(?<=_)(L|R|l|r)$", r"^(L|R|l|r)(?=_)",
    r"(?<=_)(Left|Right|left|right|LEFT|RIGHT)(?=_)", r"(?<=_)(Left|Right|left|right|LEFT|RIGHT)$", r"^(Left|Right|left|right|LEFT|RIGHT)(?=_)",
    r"(?<=_)(Lf|Rt|lf|rt|LF|RT)(?=_)", r"(?<=_)(Lf|Rt|lf|rt|LF|RT)$", r"^(Lf|Rt|lf|rt|LF|RT)(?=_)",
    r"(?<=Rig)(L|R|l|r)", r"(?<=Rig)(Left|Right|left|right|LEFT|RIGHT)", r"(?<=Rig)(Lf|Rt|lf|rt|LF|RT)",
    r"^(Left|Right|left|right|LEFT|RIGHT)", r"^(L|R|l|r)(?=[A-Z])", r"^(Lf|Rt|lf|rt|LF|RT)(?=[A-Z])",
)


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label="Node"):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _long_name(cmds, node):
    matches = cmds.ls(node, long=True) or []
    if not matches:
        raise ValueError("Node does not exist: {0}".format(node))
    return matches[0]


def _short_name(node):
    return node.rsplit("|", 1)[-1]


def _leaf_without_namespace(node):
    return _short_name(node).rsplit(":", 1)[-1]


def _uuid(cmds, node):
    values = cmds.ls(node, uuid=True) or []
    if not values:
        raise ValueError("Unable to resolve UUID for node: {0}".format(node))
    return values[0]


def _from_uuid(cmds, uuid):
    values = cmds.ls(uuid, long=True) or []
    if not values:
        raise ValueError("Unable to resolve node UUID: {0}".format(uuid))
    return values[0]


def _validate_attribute_name(attribute):
    attribute = (attribute or "").strip()
    if not attribute or "." in attribute:
        raise ValueError("Attribute must be a non-empty attribute name, not a node.attr plug.")
    return attribute


def _validate_namespace(namespace):
    namespace = (namespace or "").strip().strip(":")
    if not namespace:
        raise ValueError("Namespace must be non-empty and cannot be the root namespace.")
    if ":" in namespace:
        raise ValueError("Nested namespace paths are not supported by this primitive.")
    return namespace


def sanitize_legacy_name(name):
    """Return the legacy-compatible safe name token used for imported FBX-style names."""
    if name is None:
        raise ValueError("Name is required.")
    result = str(name)
    for token in _LEGACY_NAME_REPLACEMENTS:
        result = result.replace(token, "_")
    return result


def mirror_name(name):
    """Return the opposite-side name while preserving DAG path and namespace context.

    The token rules intentionally preserve MayaScriptNew GetMirrorName parity, but
    only the leaf name is inspected so parent paths and namespaces are never
    accidentally rewritten.
    """
    if name is None:
        raise ValueError("Name is required.")
    value = str(name)
    if not value:
        raise ValueError("Name must be non-empty.")
    path_prefix, leaf = value.rsplit("|", 1) if "|" in value else ("", value)
    namespace, base = leaf.rsplit(":", 1) if ":" in leaf else ("", leaf)
    mirrored = base
    for pattern in _MIRROR_PATTERNS:
        match = re.search(pattern, base)
        if match:
            token = match.group(1)
            start, end = match.span(1)
            mirrored = base[:start] + _MIRROR_SWAP[token] + base[end:]
            break
    leaf_result = (namespace + ":" if namespace else "") + mirrored
    return (path_prefix + "|" if path_prefix else "") + leaf_result


def resolve_mirror_pairs(nodes, require_existing=True):
    """Build a non-mutating source/target mirror plan for explicit DAG nodes.

    Counterparts are resolved in the same DAG parent and namespace. This avoids
    ambiguous global short-name lookups when rigs contain repeated leaf names.
    """
    cmds = _cmds(); nodes = list(nodes or [])
    if not nodes:
        raise ValueError("At least one node is required.")
    canonical = []
    seen = set()
    for node in nodes:
        _require_node(cmds, node, "Mirror source")
        source = _long_name(cmds, node)
        if source in seen:
            raise ValueError("Duplicate mirror source is not allowed: {0}".format(node))
        seen.add(source); canonical.append(source)
    result = []
    for source in canonical:
        mirrored_path = mirror_name(source)
        if mirrored_path == source:
            if require_existing:
                raise ValueError("Mirror naming pattern was not found: {0}".format(source))
            result.append({"source": source, "target": None, "mirror_name": mirrored_path, "status": "unmapped"})
            continue
        matches = cmds.ls(mirrored_path, long=True) or []
        if not matches:
            if require_existing:
                raise ValueError("Mirror counterpart does not exist: {0}".format(mirrored_path))
            result.append({"source": source, "target": None, "mirror_name": mirrored_path, "status": "missing"})
            continue
        if len(matches) != 1:
            raise ValueError("Mirror counterpart is ambiguous: {0}".format(mirrored_path))
        result.append({"source": source, "target": matches[0], "mirror_name": mirrored_path, "status": "ready"})
    return tuple(result)


def ensure_namespace(namespace):
    """Create one explicit top-level Maya namespace when missing and return its name."""
    cmds = _cmds(); namespace = _validate_namespace(namespace)
    if not cmds.namespace(exists=namespace):
        cmds.namespace(add=namespace)
    return namespace


def move_nodes_to_namespace(nodes, namespace):
    """Move explicit DAG nodes into a top-level namespace by renaming their leaf names."""
    cmds = _cmds(); namespace = ensure_namespace(namespace); nodes = list(nodes or [])
    if not nodes:
        raise ValueError("At least one node is required.")
    records = []
    for index, node in enumerate(nodes):
        _require_node(cmds, node)
        long_node = _long_name(cmds, node)
        records.append((index, long_node, _uuid(cmds, long_node)))
    for _, node, _ in sorted(records, key=lambda item: item[1].count("|"), reverse=True):
        cmds.rename(node, "{0}:{1}".format(namespace, _leaf_without_namespace(node)))
    return tuple(_from_uuid(cmds, uuid) for _, _, uuid in sorted(records))


def remove_namespace(namespace, merge_to_root=True):
    """Remove an explicit top-level namespace, optionally merging its members into root."""
    cmds = _cmds(); namespace = _validate_namespace(namespace)
    if not cmds.namespace(exists=namespace):
        return False
    if merge_to_root:
        cmds.namespace(moveNamespace=(namespace, ":"), force=True)
    cmds.namespace(removeNamespace=namespace)
    return True


def hierarchy_nodes(root, node_type="joint"):
    """Return root plus descendants in parent-to-child order for an explicit hierarchy."""
    cmds = _cmds(); _require_node(cmds, root, "Hierarchy root")
    root = _long_name(cmds, root)
    if node_type and cmds.nodeType(root) != node_type:
        raise ValueError("Hierarchy root has unexpected type: {0}".format(cmds.nodeType(root)))
    descendants = cmds.listRelatives(root, allDescendents=True, fullPath=True, type=node_type) or []
    return tuple([root] + list(reversed(descendants)))


def snapshot_names(nodes, attribute="nameTemp"):
    """Store each node's current short name on a string attribute and return the snapshot."""
    cmds = _cmds(); nodes = list(nodes or []); attribute = _validate_attribute_name(attribute)
    if not nodes:
        raise ValueError("At least one node is required.")
    result = []
    for node in nodes:
        _require_node(cmds, node)
        node = _long_name(cmds, node)
        value = _short_name(node)
        if not cmds.attributeQuery(attribute, node=node, exists=True):
            cmds.addAttr(node, longName=attribute, dataType="string")
        cmds.setAttr("{0}.{1}".format(node, attribute), value, type="string")
        result.append((node, value))
    return tuple(result)


def sanitize_hierarchy_names(root, storage_attribute="realName"):
    """Snapshot and sanitize one joint hierarchy without relying on Maya selection state."""
    cmds = _cmds(); storage_attribute = _validate_attribute_name(storage_attribute)
    nodes = hierarchy_nodes(root, node_type="joint")
    snapshot_names(nodes, attribute=storage_attribute)
    records = [(index, node, _uuid(cmds, node)) for index, node in enumerate(nodes)]
    for _, node, _ in sorted(records, key=lambda item: item[1].count("|"), reverse=True):
        cmds.rename(node, sanitize_legacy_name(_short_name(node)))
    resolved = tuple(_from_uuid(cmds, uuid) for _, _, uuid in sorted(records))
    return {"root": resolved[0], "nodes": resolved, "attribute": storage_attribute}


def restore_names(nodes, attribute="nameTemp", remove_attribute=False):
    """Restore explicit nodes from a stored short-name attribute, descendant-first."""
    cmds = _cmds(); nodes = list(nodes or []); attribute = _validate_attribute_name(attribute)
    if not nodes:
        raise ValueError("At least one node is required.")
    records = []
    for index, node in enumerate(nodes):
        _require_node(cmds, node)
        node = _long_name(cmds, node)
        records.append((index, node, _uuid(cmds, node)))
    for _, node, uuid in sorted(records, key=lambda item: item[1].count("|"), reverse=True):
        current = _from_uuid(cmds, uuid)
        if not cmds.attributeQuery(attribute, node=current, exists=True):
            raise ValueError("Stored name attribute is missing on {0}: {1}".format(current, attribute))
        original = cmds.getAttr("{0}.{1}".format(current, attribute))
        if not original:
            raise ValueError("Stored name is empty on {0}: {1}".format(current, attribute))
        renamed = cmds.rename(current, original)
        if remove_attribute:
            cmds.deleteAttr("{0}.{1}".format(renamed, attribute))
    return tuple(_from_uuid(cmds, uuid) for _, _, uuid in sorted(records))


def restore_hierarchy_names(root, attribute="realName", remove_attribute=False):
    """Restore names for one explicit joint hierarchy from a stored name attribute."""
    return restore_names(hierarchy_nodes(root, node_type="joint"), attribute=attribute, remove_attribute=remove_attribute)
