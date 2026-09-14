from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import naming as naming_module


def _naming():
    return importlib.reload(naming_module)


def run_setup_naming_namespace_smoke():
    naming = _naming(); cmds.file(new=True, force=True)

    cmds.select(clear=True)
    root = cmds.joint(name="RootFBXASC032Joint")
    child = cmds.joint(name="ChildFBXASC046Joint")
    original = (root, child)

    result = naming.sanitize_hierarchy_names(root)
    if len(result["nodes"]) != 2:
        raise RuntimeError("Sanitized hierarchy count mismatch.")
    if not all(cmds.objExists(node) for node in result["nodes"]):
        raise RuntimeError("Sanitized hierarchy returned stale DAG paths.")
    if result["nodes"][0].rsplit("|", 1)[-1] != "Root_Joint":
        raise RuntimeError("Root legacy name was not sanitized.")
    if result["nodes"][1].rsplit("|", 1)[-1] != "Child_Joint":
        raise RuntimeError("Child legacy name was not sanitized.")

    restored = naming.restore_hierarchy_names(result["root"], attribute="realName")
    if tuple(node.rsplit("|", 1)[-1] for node in restored) != original:
        raise RuntimeError("Hierarchy names were not restored from realName attributes.")

    moved = naming.move_nodes_to_namespace(restored, "RigTest")
    if not cmds.namespace(exists="RigTest"):
        raise RuntimeError("Namespace was not created.")
    if not all(cmds.objExists(node) for node in moved):
        raise RuntimeError("Namespace move returned stale DAG paths.")
    if not all(node.rsplit("|", 1)[-1].startswith("RigTest:") for node in moved):
        raise RuntimeError("Nodes were not moved into the requested namespace.")

    if not naming.remove_namespace("RigTest", merge_to_root=True):
        raise RuntimeError("Namespace removal did not report success.")
    if cmds.namespace(exists="RigTest"):
        raise RuntimeError("Namespace still exists after merge/remove.")
    if not cmds.objExists("RootFBXASC032Joint") or not cmds.objExists("ChildFBXASC046Joint"):
        raise RuntimeError("Namespace merge did not preserve hierarchy nodes.")

    return "SETUP_NAMING_NAMESPACE_SMOKE_OK:4"
