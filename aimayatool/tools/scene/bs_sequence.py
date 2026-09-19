from __future__ import absolute_import


_TRANSFORM_ATTRS = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")


def _cmds():
    import maya.cmds as cmds
    return cmds


def collect_transform_keyframes(node):
    """Return sorted non-zero transform key times for one explicit node."""
    cmds = _cmds()
    if not node or not cmds.objExists(node):
        return tuple()
    frames = set()
    for attr in _TRANSFORM_ATTRS:
        plug = "{0}.{1}".format(node, attr)
        if not cmds.objExists(plug):
            continue
        frames.update(cmds.keyframe(plug, query=True, timeChange=True) or [])
    return tuple(sorted(frame for frame in frames if frame != 0))


def _ensure_double_attr(cmds, node, attr, minimum=0.0, maximum=10.0, default=0.0):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType="double", minValue=minimum, maxValue=maximum, defaultValue=default)
    cmds.setAttr("{0}.{1}".format(node, attr), edit=True, keyable=True)
    return "{0}.{1}".format(node, attr)


def _ensure_bool_attr(cmds, node, attr, default=False):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType="bool", defaultValue=bool(default))
    cmds.setAttr("{0}.{1}".format(node, attr), edit=True, keyable=True)
    return "{0}.{1}".format(node, attr)


def _ensure_proxy_attr(cmds, node, attr, source_plug, attribute_type="double"):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType=attribute_type, proxy=source_plug)
    plug = "{0}.{1}".format(node, attr)
    cmds.setAttr(plug, edit=True, keyable=True)
    return plug


def build_bs_sequence_from_object_keys(item):
    """Build the legacy ScenePattern BS sequence workflow from one explicit descriptor."""
    cmds = _cmds()
    data = dict(item or {})
    mesh = str(data.get("mesh") or "").strip()
    mesh_animation = str(data.get("meshAnimation") or "").strip()
    object_animation = str(data.get("objectAnimation") or "").strip()
    joint_holder = str(data.get("jointHolder") or "").strip()
    attr = str(data.get("attr") or "").strip()
    bs_parent = str(data.get("bsParent") or "").strip()
    holders_raw = data.get("attrHolder") or data.get("attrHolders") or ()
    if isinstance(holders_raw, str):
        holders = [value.strip() for value in holders_raw.splitlines() if value.strip()]
    else:
        holders = [str(value).strip() for value in holders_raw if str(value).strip()]
    holders = [node for node in holders if cmds.objExists(node)]

    for label, node in (("mesh", mesh), ("meshAnimation", mesh_animation), ("jointHolder", joint_holder)):
        if not node or not cmds.objExists(node):
            return {"status": "skipped_missing_{0}".format(label), label: node}
    if not object_animation or not cmds.objExists(object_animation):
        return {"status": "skipped_missing_objectAnimation", "objectAnimation": object_animation}
    if not holders:
        return {"status": "skipped_missing_attrHolder", "mesh": mesh}
    if not attr:
        raise ValueError("BS Sequence requires attr.")

    keyframes = collect_transform_keyframes(object_animation)
    if not keyframes:
        return {"status": "skipped_no_keyframes", "objectAnimation": object_animation}

    current_frame = cmds.currentTime(query=True)
    generated = []
    try:
        for index, frame in enumerate(keyframes, 1):
            cmds.currentTime(frame, edit=True)
            duplicate = cmds.duplicate(mesh_animation, rr=True, inputConnections=False, upstreamNodes=False)[0]
            duplicate = cmds.rename(duplicate, "{0}_Shoot_{1:02d}".format(mesh.split("|")[-1], index))
            generated.append(duplicate)
    finally:
        cmds.currentTime(current_frame, edit=True)

    group_name = "{0}_BSs".format(mesh.split("|")[-1])
    if cmds.objExists(group_name):
        cmds.delete(group_name)
    bs_group = cmds.group(generated, name=group_name)
    if bs_parent and cmds.objExists(bs_parent):
        bs_group = cmds.parent(bs_group, bs_parent)[0]

    blend_name = "{0}_{1}_BS".format(mesh.split("|")[-1], attr)
    if cmds.objExists(blend_name):
        cmds.delete(blend_name)
    blend_shape = cmds.blendShape(generated, mesh, name=blend_name)[0]

    main_holder = holders[0]
    main_attr = _ensure_double_attr(cmds, main_holder, attr)
    for holder in holders[1:]:
        _ensure_proxy_attr(cmds, holder, attr, main_attr)

    joint_attr = _ensure_double_attr(cmds, joint_holder, attr)
    if not cmds.isConnected(main_attr, joint_attr):
        cmds.connectAttr(main_attr, joint_attr, force=True)

    count = len(generated)
    segment = 10.0 / float(count)
    cmds.setAttr(main_attr, 0.0)
    for index in range(count):
        plug = "{0}.w[{1}]".format(blend_shape, index)
        cmds.setAttr(plug, 0.0)
        cmds.setDrivenKeyframe(plug, currentDriver=main_attr)

    for step in range(count):
        driver_value = segment * (step + 1)
        if step == count - 1:
            driver_value -= segment * 0.5
        cmds.setAttr(main_attr, driver_value)
        for index in range(count):
            plug = "{0}.w[{1}]".format(blend_shape, index)
            value = 1.0 if index == step else 0.5 if index in (step - 1, step + 1) else 0.0
            cmds.setAttr(plug, value)
            cmds.setDrivenKeyframe(plug, currentDriver=main_attr)

    cmds.setAttr(main_attr, 10.0)
    for index in range(count):
        plug = "{0}.w[{1}]".format(blend_shape, index)
        cmds.setAttr(plug, 0.0)
        cmds.setDrivenKeyframe(plug, currentDriver=main_attr)

    show_attr_name = "{0}ShowBS".format(attr)
    main_show_attr = _ensure_bool_attr(cmds, main_holder, show_attr_name)
    for holder in holders[1:]:
        _ensure_proxy_attr(cmds, holder, show_attr_name, main_show_attr, attribute_type="bool")
    visibility = bs_group + ".visibility"
    if not cmds.isConnected(main_show_attr, visibility):
        cmds.connectAttr(main_show_attr, visibility, force=True)

    cmds.setAttr(main_attr, 0.0)
    cmds.currentTime(current_frame, edit=True)
    return {
        "status": "applied",
        "mesh": mesh,
        "keyframes": keyframes,
        "generated_meshes": tuple(generated),
        "group": bs_group,
        "blend_shape": blend_shape,
        "driver": main_attr,
        "show_driver": main_show_attr,
    }


def execute_bs_sequence_items(items):
    return tuple(build_bs_sequence_from_object_keys(item) for item in tuple(items or ()))


def bs_sequence_managed_maya_smoke():
    cmds = _cmds()
    cmds.file(new=True, force=True)
    target = cmds.polyCube(name="AIBridgeBSTarget")[0]
    animated = cmds.polyCube(name="AIBridgeBSAnimated")[0]
    driver_obj = cmds.createNode("transform", name="AIBridgeBSAnimDriver")
    main_holder = cmds.createNode("transform", name="AIBridgeBSMain")
    proxy_holder = cmds.createNode("transform", name="AIBridgeBSProxy")
    joint_holder = cmds.createNode("transform", name="AIBridgeBSJoint")
    cmds.setKeyframe(driver_obj, attribute="tx", time=0, value=0)
    cmds.setKeyframe(driver_obj, attribute="tx", time=5, value=1)
    cmds.setKeyframe(driver_obj, attribute="tx", time=10, value=2)
    cmds.currentTime(3, edit=True)
    before = cmds.currentTime(query=True)
    result = build_bs_sequence_from_object_keys({
        "mesh": target, "meshAnimation": animated, "objectAnimation": driver_obj,
        "attrHolder": main_holder + "\n" + proxy_holder, "jointHolder": joint_holder,
        "attr": "sequence", "bsParent": ""
    })
    after = cmds.currentTime(query=True)
    generated = list(result.get("generated_meshes") or ())
    blend = result.get("blend_shape")
    group = result.get("group")
    driver = result.get("driver")
    show_driver = result.get("show_driver")
    joint_plug = joint_holder + ".sequence"
    proxy_plug = proxy_holder + ".sequence"
    show_proxy = proxy_holder + ".sequenceShowBS"
    driven_curves = cmds.listConnections(blend, source=True, destination=False, type="animCurve") or []
    checks = {
        "status": result.get("status") == "applied",
        "keyframes": tuple(result.get("keyframes") or ()) == (5.0, 10.0),
        "generated": len(generated) == 2 and all(cmds.objExists(x) for x in generated),
        "names": [x.split("|")[-1] for x in generated] == [target + "_Shoot_01", target + "_Shoot_02"],
        "group": bool(group and cmds.objExists(group)),
        "blend_shape": bool(blend and cmds.objExists(blend)),
        "joint_connected": bool(driver and cmds.isConnected(driver, joint_plug)),
        "proxy": cmds.objExists(proxy_plug) and cmds.attributeQuery("sequence", node=proxy_holder, exists=True),
        "show_proxy": cmds.objExists(show_proxy) and bool(show_driver),
        "visibility_connected": bool(show_driver and group and cmds.isConnected(show_driver, group + ".visibility")),
        "driven_keys": bool(driven_curves),
        "frame_restored": before == after == 3.0,
    }
    return {"success": all(checks.values()), "checks": checks, "result": result}
