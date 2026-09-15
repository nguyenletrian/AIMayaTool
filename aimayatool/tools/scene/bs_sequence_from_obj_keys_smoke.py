from __future__ import absolute_import


def run_bs_sequence_from_obj_keys_smoke():
    import maya.cmds as cmds
    from .bs_sequence_from_obj_keys import build_bs_sequence_plan, execute_bs_sequence

    cmds.file(new=True, force=True)
    base = cmds.polyCube(name="AIBSSequenceMesh")[0]
    animated = cmds.duplicate(base, name="AIBSSequenceAnimated")[0]
    animated_shape = (cmds.listRelatives(animated, shapes=True, noIntermediate=True, fullPath=True) or [None])[0]
    main_holder = cmds.createNode("transform", name="AIBSSequenceMain_CTRL")
    proxy_holder = cmds.createNode("transform", name="AIBSSequenceProxy_CTRL")
    joint_holder = cmds.createNode("transform", name="AIBSSequence_JNT")
    parent = cmds.createNode("transform", name="AIBSSequence_ROOT")
    if not animated_shape:
        raise AssertionError("Animated mesh has no renderable shape.")

    cmds.currentTime(7, edit=True)
    plan = build_bs_sequence_plan(base, "Expression", (5, 10))
    result = execute_bs_sequence(
        plan,
        animated,
        animated_shape + ".outMesh",
        (main_holder, proxy_holder),
        joint_holder,
        bs_parent=parent,
        cmds_module=cmds,
    )

    generated = tuple(result.get("generated_meshes") or ())
    if len(generated) != 2 or not all(cmds.objExists(node) for node in generated):
        raise AssertionError("Expected two sampled meshes: {0}".format(generated))
    group = result["group"]
    if (cmds.listRelatives(group, parent=True) or []) != [parent]:
        raise AssertionError("BS group parent mismatch.")
    blend = result["blendshape"]
    if not cmds.objExists(blend) or cmds.nodeType(blend) != "blendShape":
        raise AssertionError("BlendShape was not created.")

    driver = result["driver"]
    proxy_driver = proxy_holder + ".Expression"
    joint_driver = joint_holder + ".Expression"
    show = result["show"]
    proxy_show = proxy_holder + ".ExpressionShowBS"
    if not all(cmds.objExists(plug) for plug in (driver, proxy_driver, joint_driver, show, proxy_show)):
        raise AssertionError("Expected driver/proxy/joint/show attributes are missing.")
    if not cmds.isConnected(driver, joint_driver):
        raise AssertionError("Main driver is not connected to joint holder.")
    if not cmds.isConnected(show, group + ".visibility"):
        raise AssertionError("ShowBS is not connected to group visibility.")

    for index in range(2):
        plug = "{0}.w[{1}]".format(blend, index)
        incoming = cmds.listConnections(plug, source=True, destination=False, type="animCurve") or []
        if not incoming:
            raise AssertionError("BlendShape weight {0} has no driven-key curve.".format(index))

    if cmds.currentTime(query=True) != 7.0:
        raise AssertionError("Current frame was not restored.")
    if abs(float(cmds.getAttr(driver))) > 1e-8:
        raise AssertionError("Driver value was not restored to zero.")

    cmds.setAttr(show, True)
    if not cmds.getAttr(group + ".visibility"):
        raise AssertionError("ShowBS visibility connection does not evaluate true.")
    cmds.setAttr(show, False)
    if cmds.getAttr(group + ".visibility"):
        raise AssertionError("ShowBS visibility connection does not evaluate false.")

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_BS_SEQUENCE_TRANSACTION_OK:2"
