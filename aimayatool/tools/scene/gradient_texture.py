from __future__ import absolute_import


def normalize_gradient_texture(data):
    data = data or {}
    obj = str(data.get("object", "")).strip()
    obj_connect = str(data.get("objConnect", "")).strip()
    attr_connect = str(data.get("attrConnect", "")).strip()
    if not obj:
        raise ValueError("object must not be empty")
    if not obj_connect or not attr_connect:
        raise ValueError("objConnect and attrConnect must not be empty")
    ramp_type = int(data.get("type", 0))
    interpolation = int(data.get("interpolation", 0))
    white_begin = float(data.get("whiteBegin", 0.0))
    black_begin = float(data.get("blackBegin", 1.0))
    run_color = str(data.get("runColor", "white")).strip().lower()
    if run_color in ("0", "black"):
        run_index = 1
    elif run_color in ("1", "white"):
        run_index = 0
    else:
        raise ValueError("runColor must be white/black or 1/0")
    minimum = float(data.get("minValue", 0.0))
    maximum = float(data.get("maxValue", 1.0))
    reverse = bool(data.get("reverse", False))
    return {
        "object": obj,
        "type": ramp_type,
        "interpolation": interpolation,
        "whiteBegin": white_begin,
        "blackBegin": black_begin,
        "runColor": run_color,
        "runIndex": run_index,
        "minValue": minimum,
        "maxValue": maximum,
        "objConnect": obj_connect,
        "attrConnect": attr_connect,
        "driverAttr": obj_connect + "." + attr_connect,
        "reverse": reverse,
        "inputMin": 10.0 if reverse else 0.0,
        "inputMax": 0.0 if reverse else 10.0,
        "ramp": obj + "_ramp",
        "remap": obj + "_remapValue",
    }


def _shape(cmds, node):
    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []
    if not shapes:
        raise ValueError("Missing shape: " + node)
    return shapes[0]


def _material(cmds, shape):
    shading_groups = cmds.listConnections(shape, source=False, destination=True, type="shadingEngine") or []
    if not shading_groups:
        raise ValueError("Missing shading group for: " + shape)
    materials = cmds.ls(cmds.listConnections(shading_groups[0] + ".surfaceShader", source=True, destination=False) or [], materials=True) or []
    if not materials:
        raise ValueError("Missing material for shading group: " + shading_groups[0])
    return shading_groups[0], materials[0]


def apply_gradient_texture(data):
    import maya.cmds as cmds

    plan = normalize_gradient_texture(data)
    if not cmds.objExists(plan["object"]):
        raise ValueError("Missing object: " + plan["object"])
    if not cmds.objExists(plan["objConnect"]):
        raise ValueError("Missing objConnect: " + plan["objConnect"])
    shape = _shape(cmds, plan["object"])
    shading_group, material = _material(cmds, shape)
    ramp = cmds.shadingNode("ramp", asTexture=True, name=plan["ramp"])
    cmds.setAttr(ramp + ".type", plan["type"])
    cmds.setAttr(ramp + ".interpolation", plan["interpolation"])
    cmds.setAttr(ramp + ".colorEntryList[0].color", 1, 1, 1, type="double3")
    cmds.setAttr(ramp + ".colorEntryList[0].position", plan["whiteBegin"])
    cmds.setAttr(ramp + ".colorEntryList[1].color", 0, 0, 0, type="double3")
    cmds.setAttr(ramp + ".colorEntryList[1].position", plan["blackBegin"])
    output = material + (".transparency" if cmds.attributeQuery("transparency", node=material, exists=True) else ".opacity")
    if not cmds.objExists(output):
        raise ValueError("Material has neither transparency nor opacity: " + material)
    cmds.connectAttr(ramp + ".outColor", output, force=True)
    if not cmds.attributeQuery(plan["attrConnect"], node=plan["objConnect"], exists=True):
        cmds.addAttr(plan["objConnect"], longName=plan["attrConnect"], attributeType="double", minValue=0, maxValue=10, defaultValue=0, keyable=True)
    remap = cmds.createNode("remapValue", name=plan["remap"])
    cmds.setAttr(remap + ".inputMin", plan["inputMin"])
    cmds.setAttr(remap + ".inputMax", plan["inputMax"])
    cmds.setAttr(remap + ".outputMin", plan["minValue"])
    cmds.setAttr(remap + ".outputMax", plan["maxValue"])
    cmds.connectAttr(plan["driverAttr"], remap + ".inputValue", force=True)
    position = ramp + ".colorEntryList[%d].position" % plan["runIndex"]
    cmds.connectAttr(remap + ".outValue", position, force=True)
    return {"plan": plan, "shape": shape, "shadingGroup": shading_group, "material": material, "ramp": ramp, "remap": remap, "position": position}


def gradient_texture_managed_maya_smoke():
    import maya.cmds as cmds

    obj = cmds.polyPlane(name="AIBridgeGradientMesh")[0]
    shader = cmds.shadingNode("lambert", asShader=True, name="AIBridgeGradientMaterial")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="AIBridgeGradientSG")
    cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(obj, edit=True, forceElement=sg)
    driver = cmds.createNode("transform", name="AIBridgeGradientDriver")
    result = apply_gradient_texture({"object": obj, "type": 0, "interpolation": 1, "whiteBegin": 0.2, "blackBegin": 0.8, "runColor": "white", "minValue": 0.1, "maxValue": 0.9, "objConnect": driver, "attrConnect": "gradient", "reverse": False})
    checks = {
        "ramp": cmds.objExists(result["ramp"]),
        "remap": cmds.objExists(result["remap"]),
        "driver": cmds.isConnected(driver + ".gradient", result["remap"] + ".inputValue"),
        "position": cmds.isConnected(result["remap"] + ".outValue", result["position"]),
        "material": cmds.isConnected(result["ramp"] + ".outColor", shader + ".transparency"),
    }
    if not all(checks.values()):
        raise RuntimeError("GradientTexture smoke failed: {0}".format(checks))
    return {"ok": True, "checks": checks}
