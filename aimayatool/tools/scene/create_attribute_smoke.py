from __future__ import absolute_import


def run_scene_create_attribute_smoke():
    from maya import cmds
    from aimayatool.tools.scene.create_attribute import create_attribute

    a = cmds.createNode("transform", name="Attr_A_CTRL")
    b = cmds.createNode("transform", name="Attr_B_CTRL")

    result = create_attribute(
        [a, b, "Missing_CTRL"],
        "twistAmount",
        attr_type="double",
        keyable=False,
        lock=True,
        channel_box=True,
        minimum=-2.0,
        maximum=5.0,
        default=1.5,
    )
    if tuple(item["status"] for item in result) != ("created", "created", "missing"):
        raise AssertionError("Create Attribute statuses are incorrect: {0}".format(result))

    for obj in (a, b):
        plug = obj + ".twistAmount"
        if not cmds.objExists(plug):
            raise AssertionError("Attribute was not created on {0}".format(obj))
        if abs(cmds.addAttr(plug, query=True, defaultValue=True) - 1.5) > 1e-8:
            raise AssertionError("Default value mismatch on {0}".format(obj))
        if abs(cmds.attributeQuery("twistAmount", node=obj, minimum=True)[0] + 2.0) > 1e-8:
            raise AssertionError("Minimum mismatch on {0}".format(obj))
        if abs(cmds.attributeQuery("twistAmount", node=obj, maximum=True)[0] - 5.0) > 1e-8:
            raise AssertionError("Maximum mismatch on {0}".format(obj))
        if not cmds.getAttr(plug, lock=True):
            raise AssertionError("Lock state was not applied to {0}".format(obj))
        if cmds.getAttr(plug, keyable=True):
            raise AssertionError("Attribute should not be keyable on {0}".format(obj))
        if not cmds.getAttr(plug, channelBox=True):
            raise AssertionError("Channel-box state was not applied to {0}".format(obj))

    existing = create_attribute([a], "twistAmount", attr_type="double")
    if existing[0]["status"] != "exists":
        raise AssertionError("Existing attribute was not skipped deterministically.")

    enum_result = create_attribute([a], "mode", attr_type="enum", enum="FK:IK:Both", keyable=True)
    if enum_result[0]["status"] != "created":
        raise AssertionError("Enum attribute was not created.")
    enum_names = cmds.attributeQuery("mode", node=a, listEnum=True) or []
    if enum_names != ["FK:IK:Both"]:
        raise AssertionError("Enum names mismatch: {0}".format(enum_names))

    return "AIBRIDGE_UI_SMOKE_OK:SCENE_CREATE_ATTRIBUTE_OK:2"
