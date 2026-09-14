from __future__ import absolute_import


def run_scene_bs_sequence_smoke():
    import maya.cmds as cmds
    from .bs_sequence import build_bs_sequence_from_object_keys

    cmds.file(new=True, force=True)
    base = cmds.polyCube(name="FaceMesh")[0]
    animated = cmds.duplicate(base, name="FaceMesh_Animated")[0]
    object_anim = cmds.createNode("transform", name="FaceDriver")
    main_holder = cmds.createNode("transform", name="FaceAttrs_CTRL")
    proxy_holder = cmds.createNode("transform", name="FaceProxy_CTRL")
    joint_holder = cmds.createNode("transform", name="Face_JNT")
    parent = cmds.createNode("transform", name="BS_ROOT")

    cmds.setKeyframe(object_anim + ".tx", time=0, value=0)
    cmds.setKeyframe(object_anim + ".tx", time=5, value=1)
    cmds.setKeyframe(object_anim + ".ry", time=10, value=20)
    cmds.currentTime(3, edit=True)

    result = build_bs_sequence_from_object_keys({
        "mesh": base,
        "meshAnimation": animated,
        "objectAnimation": object_anim,
        "attrHolder": main_holder + "\n" + proxy_holder,
        "jointHolder": joint_holder,
        "attr": "Expression",
        "bsParent": parent,
    })
    if result.get("status") != "applied":
        raise AssertionError("BS sequence did not apply: {0}".format(result))
    if tuple(result.get("keyframes") or ()) != (5.0, 10.0):
        raise AssertionError("Unexpected BS sequence keyframes: {0}".format(result.get("keyframes")))
    generated = tuple(result.get("generated_meshes") or ())
    if len(generated) != 2 or not all(cmds.objExists(node) for node in generated):
        raise AssertionError("Expected two generated BS meshes: {0}".format(generated))
    group = result["group"]
    group_parent = cmds.listRelatives(group, parent=True) or []
    if group_parent != [parent]:
        raise AssertionError("BS group parent mismatch: {0}".format(group_parent))
    blend = result["blend_shape"]
    if not cmds.objExists(blend) or cmds.nodeType(blend) != "blendShape":
        raise AssertionError("BlendShape was not created: {0}".format(blend))
    if not cmds.attributeQuery("Expression", node=main_holder, exists=True):
        raise AssertionError("Main driver attribute missing.")
    if not cmds.attributeQuery("Expression", node=proxy_holder, exists=True):
        raise AssertionError("Proxy driver attribute missing.")
    if not cmds.isConnected(main_holder + ".Expression", joint_holder + ".Expression"):
        raise AssertionError("Main driver is not connected to joint holder.")
    if not cmds.attributeQuery("ExpressionShowBS", node=main_holder, exists=True):
        raise AssertionError("Show BS attribute missing.")
    if not cmds.isConnected(main_holder + ".ExpressionShowBS", group + ".visibility"):
        raise AssertionError("Show BS attribute is not driving group visibility.")
    for index in range(2):
        curves = cmds.listConnections("{0}.w[{1}]".format(blend, index), source=True, destination=False, type="animCurve") or []
        if not curves:
            curves = cmds.listConnections("{0}.w[{1}]".format(blend, index), source=True, destination=False) or []
        if not curves:
            raise AssertionError("BlendShape weight {0} has no driven-key input.".format(index))
    if cmds.currentTime(query=True) != 3.0:
        raise AssertionError("Current frame was not restored.")

    skipped = build_bs_sequence_from_object_keys({
        "mesh": base,
        "meshAnimation": animated,
        "objectAnimation": "MissingAnimation",
        "attrHolder": main_holder,
        "jointHolder": joint_holder,
        "attr": "Missing",
    })
    if skipped.get("status") != "skipped_missing_objectAnimation":
        raise AssertionError("Missing animation was not skipped deterministically: {0}".format(skipped))

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_BS_SEQUENCE_OK:2"
