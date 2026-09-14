from __future__ import absolute_import


_LEGACY_NAME_REPLACEMENTS = ("FBXASC046", "FBXASC045", "FBXASC032", "[", "]", ".")


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
    long_nodes = []
    for node in nodes:
        _require_node(cmds, node)
        long_nodes.append(_long_name(cmds, node))
    # Rename deepest nodes first so ancestor path changes do not invalidate descendants.
    result = []
    for node in sorted(long_nodes, key=lambda value: value.count("|"), reverse=True):
        renamed = cmds.rename(node, "{0}:{1}".format(namespace, _leaf_without_namespace(node)))
        result.append(_long_name(cmds, renamed))
    result.reverse()
    return tuple(result)


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
    renamed = []
    # Descendant-first rename prevents stale DAG paths while parents are renamed.
    for node in sorted(nodes, key=lambda value: value.count("|"), reverse=True):
        safe_name = sanitize_legacy_name(_short_name(node))
        renamed_node = cmds.rename(node, safe_name)
        renamed.append(_long_name(cmds, renamed_node))
    renamed.reverse()
    root_candidates = [node for node in renamed if node.count("|") == min(item.count("|") for item in renamed)]
    return {"root": root_candidates[0], "nodes": tuple(renamed), "attribute": storage_attribute}


def restore_names(nodes, attribute="nameTemp", remove_attribute=False):
    """Restore explicit nodes from a stored short-name attribute, descendant-first."""
    cmds = _cmds(); nodes = list(nodes or []); attribute = _validate_attribute_name(attribute)
    if not nodes:
        raise ValueError("At least one node is required.")
    long_nodes = []
    for node in nodes:
        _require_node(cmds, node)
        long_nodes.append(_long_name(cmds, node))
    restored = []
    for node in sorted(long_nodes, key=lambda value: value.count("|"), reverse=True):
        if not cmds.attributeQuery(attribute, node=node, exists=True):
            raise ValueError("Stored name attribute is missing on {0}: {1}".format(node, attribute))
        original = cmds.getAttr("{0}.{1}".format(node, attribute))
        if not original:
            raise ValueError("Stored name is empty on {0}: {1}".format(node, attribute))
        renamed = cmds.rename(node, original)
        if remove_attribute:
            cmds.deleteAttr("{0}.{1}".format(renamed, attribute))
        restored.append(_long_name(cmds, renamed))
    restored.reverse()
    return tuple(restored)


def restore_hierarchy_names(root, attribute="realName", remove_attribute=False):
    """Restore names for one explicit joint hierarchy from a stored name attribute."""
    return restore_names(hierarchy_nodes(root, node_type="joint"), attribute=attribute, remove_attribute=remove_attribute)
