from __future__ import absolute_import

import traceback


def _cmds():
    import maya.cmds as cmds
    return cmds


def _naming():
    from . import naming
    return naming


def _run(label, fn):
    cmds = _cmds()
    try:
        result = fn()
        text = str(result) if result else "no changes"
        cmds.inViewMessage(amg="{0}: {1}".format(label, text), pos="midCenter", fade=True)
        return result
    except Exception as exc:
        message = "{0} failed: {1}".format(label, exc)
        cmds.warning("AIMayaTool Setup: " + message)
        try:
            cmds.inViewMessage(amg="<hl>{0}</hl>".format(message), pos="midCenter", fade=True)
        except Exception:
            pass
        traceback.print_exc()
        return None


def _selection():
    return _cmds().ls(selection=True, long=True) or []


def _selected_joint_root():
    cmds = _cmds()
    nodes = _selection()
    if len(nodes) != 1 or cmds.nodeType(nodes[0]) != "joint":
        raise ValueError("Select exactly one joint hierarchy root.")
    return nodes[0]


def _selected_nodes():
    nodes = _selection()
    if not nodes:
        raise ValueError("Select one or more DAG nodes.")
    return nodes


def _selected_transforms():
    nodes = _cmds().ls(selection=True, long=True, type="transform") or []
    if not nodes:
        raise ValueError("Select one or more transforms to mirror to their named counterparts.")
    return nodes


def _mirror_selected(axis):
    return _naming().execute_mirror_transform_batch(_selected_transforms(), axis=axis)


def _preview_mirror_selected(axis):
    plan = _naming().resolve_mirror_pairs(_selected_transforms(), require_existing=False)
    counts = {"ready": 0, "missing": 0, "unmapped": 0}
    for item in plan:
        status = item.get("status", "unmapped")
        counts[status] = counts.get(status, 0) + 1
    return "{0} ready, {1} missing, {2} unmapped".format(counts.get("ready", 0), counts.get("missing", 0), counts.get("unmapped", 0))


def _prompt_namespace(title, action):
    cmds = _cmds()
    if cmds.promptDialog(title=title, message="Namespace:", text="TempNameSpace", button=[action, "Cancel"], defaultButton=action, cancelButton="Cancel", dismissString="Cancel") != action:
        return None
    namespace = cmds.promptDialog(query=True, text=True).strip()
    if not namespace:
        raise ValueError("Namespace is required.")
    return namespace


def _clean_joint_names():
    return _naming().sanitize_hierarchy_names(_selected_joint_root(), storage_attribute="realName")


def _restore_joint_names():
    return _naming().restore_hierarchy_names(_selected_joint_root(), attribute="realName")


def _save_name_temp():
    return _naming().snapshot_names(_selected_nodes(), attribute="nameTemp")


def _restore_name_temp():
    return _naming().restore_names(_selected_nodes(), attribute="nameTemp")


def _move_to_namespace():
    namespace = _prompt_namespace("Move to Namespace", "Move")
    if namespace is None:
        return None
    return _naming().move_nodes_to_namespace(_selected_nodes(), namespace)


def _remove_namespace():
    namespace = _prompt_namespace("Remove Namespace", "Remove")
    if namespace is None:
        return None
    return _naming().remove_namespace(namespace, merge_to_root=True)


def build_ui():
    cmds = _cmds()
    cmds.text(label="Names and namespaces", align="left")
    cmds.text(label="Joint clean/restore uses the selected hierarchy root. Temp-name and namespace actions use explicit selected nodes.", align="left")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Clean Joint Names", command=lambda *_: _run("Clean joint names", _clean_joint_names))
    cmds.button(label="Restore Joint Names", command=lambda *_: _run("Restore joint names", _restore_joint_names))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Save Name Temp", command=lambda *_: _run("Save name temp", _save_name_temp))
    cmds.button(label="Restore Name Temp", command=lambda *_: _run("Restore name temp", _restore_name_temp))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Move to Namespace...", command=lambda *_: _run("Move to namespace", _move_to_namespace))
    cmds.button(label="Remove Namespace...", command=lambda *_: _run("Remove namespace", _remove_namespace))
    cmds.setParent("..")

    cmds.separator(height=8, style="none")
    cmds.text(label="Mirror batch", align="left")
    cmds.text(label="Preview resolves counterparts without changing the scene. Mirror executes only after all targets pass domain preflight.", align="left")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, axis in (("Preview X", "x"), ("Preview Y", "y"), ("Preview Z", "z")):
        cmds.button(label=label, command=lambda *_, a=axis: _run("Mirror " + a.upper() + " preview", lambda: _preview_mirror_selected(a)))
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=3)
    for label, axis in (("Mirror X", "x"), ("Mirror Y", "y"), ("Mirror Z", "z")):
        cmds.button(label=label, command=lambda *_, a=axis: _run("Mirror " + a.upper(), lambda: _mirror_selected(a)))
    cmds.setParent("..")
