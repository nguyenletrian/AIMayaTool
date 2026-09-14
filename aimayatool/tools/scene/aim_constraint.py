from __future__ import absolute_import

from aimayatool.tools.setup import controls

_AXIS_MAP = {
    "x": (1.0, 0.0, 0.0),
    "-x": (-1.0, 0.0, 0.0),
    "y": (0.0, 1.0, 0.0),
    "-y": (0.0, -1.0, 0.0),
    "z": (0.0, 0.0, 1.0),
    "-z": (0.0, 0.0, -1.0),
}


def axis_vector(axis):
    key = str(axis or "").strip().lower()
    if key not in _AXIS_MAP:
        raise ValueError("Unsupported aim axis: {0}".format(axis))
    return _AXIS_MAP[key]


def build_aim_constraint_plan(descriptor):
    data = dict(descriptor or {})
    child = str(data.get("child") or "").strip()
    parent = str(data.get("parent") or "").strip()
    reference = str(data.get("reference") or "").strip()
    if not child or not parent or not reference:
        raise ValueError("Aim Constraint requires child, parent and reference.")
    return ({
        "operation": "aim_constraint",
        "child": child,
        "parent": parent,
        "reference": reference,
        "aim_vector": axis_vector(data.get("mainAxis", "x")),
        "up_vector": axis_vector(data.get("secondAxis", "y")),
        "maintain_offset": bool(data.get("maintain", True)),
        "constraint_content": str(data.get("constraintContent") or "").strip(),
    },)


def _cmds():
    import maya.cmds as cmds
    return cmds


def execute_aim_constraint_plan(plan):
    cmds = _cmds()
    results = []
    for operation in tuple(plan or ()):
        if operation.get("operation") != "aim_constraint":
            raise ValueError("Unsupported Aim Constraint operation: {0}".format(operation.get("operation")))
        child = operation["child"]
        if not cmds.objExists(child):
            results.append({"child": child, "status": "skipped_missing_child"})
            continue
        for key in ("parent", "reference"):
            node = operation[key]
            if not cmds.objExists(node):
                raise ValueError("Aim Constraint {0} does not exist: {1}".format(key, node))
        content = operation.get("constraint_content") or ""
        if content and not cmds.objExists(content):
            raise ValueError("Aim Constraint constraint_content does not exist: {0}".format(content))
        offset, child_path = controls.create_zero_group(child, suffix="_AimGrp")
        constraint = cmds.aimConstraint(
            operation["parent"],
            offset,
            aimVector=tuple(operation["aim_vector"]),
            upVector=tuple(operation["up_vector"]),
            worldUpType="object",
            worldUpObject=operation["reference"],
            mo=bool(operation.get("maintain_offset", True)),
        )[0]
        if content:
            constraint = cmds.parent(constraint, content)[0]
        results.append({
            "child": child,
            "child_path": child_path,
            "status": "applied",
            "offset": offset,
            "constraint": constraint,
        })
    return tuple(results)
