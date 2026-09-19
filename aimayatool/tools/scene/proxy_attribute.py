from __future__ import absolute_import

from aimayatool.tools.setup.proxy_attributes import create_proxy_attribute


def _text(value):
    return str(value or "").strip()


def _targets(value):
    if isinstance(value, (list, tuple)):
        values = value
    else:
        values = str(value or "").splitlines()
    return [str(x).strip() for x in values if str(x).strip()]


def build_proxy_attribute_plan(data):
    data = data or {}
    source = _text(data.get("source"))
    source_attr = _text(data.get("sourceAttr"))
    target_attr = _text(data.get("targetAttr"))
    if not source or not source_attr:
        raise ValueError("Proxy source and sourceAttr are required")
    if not target_attr:
        raise ValueError("Proxy targetAttr is required")
    return {"source_plug": source + "." + source_attr, "target_attr": target_attr, "targets": _targets(data.get("targets"))}


def apply_proxy_attribute(data, cmds_module=None):
    cmds = cmds_module
    if cmds is None:
        import maya.cmds as cmds
    plan = build_proxy_attribute_plan(data)
    if not cmds.objExists(plan["source_plug"]):
        raise ValueError("Proxy source plug does not exist: {0}".format(plan["source_plug"]))
    result = []
    for target in plan["targets"]:
        if not cmds.objExists(target):
            result.append({"target": target, "status": "skipped_missing"})
            continue
        try:
            plug = create_proxy_attribute(plan["source_plug"], target, attribute=plan["target_attr"], cmds_module=cmds)
            result.append({"target": target, "status": "created", "plug": plug})
        except ValueError as exc:
            result.append({"target": target, "status": "skipped", "error": str(exc)})
    return result


def proxy_attribute_managed_maya_smoke():
    import maya.cmds as cmds
    source = cmds.createNode("transform", name="AIBridgeProxySource")
    target_a = cmds.createNode("transform", name="AIBridgeProxyTargetA")
    target_b = cmds.createNode("transform", name="AIBridgeProxyTargetB")
    cmds.addAttr(source, longName="driver", attributeType="double", defaultValue=0.0, keyable=True)
    result = apply_proxy_attribute({"source": source, "sourceAttr": "driver", "targetAttr": "proxyDriver", "targets": target_a + "\\nMissingProxyTarget\\n" + target_b}, cmds_module=cmds)
    created = [x for x in result if x["status"] == "created"]
    missing = [x for x in result if x["status"] == "skipped_missing"]
    attrs = all(cmds.objExists(x + ".proxyDriver") for x in (target_a, target_b))
    cmds.setAttr(source + ".driver", 7.25)
    values = all(abs(cmds.getAttr(x + ".proxyDriver") - 7.25) < 1e-8 for x in (target_a, target_b))
    invalid_source = False
    try:
        apply_proxy_attribute({"source": source, "sourceAttr": "missingAttr", "targetAttr": "badProxy", "targets": target_a}, cmds_module=cmds)
    except ValueError:
        invalid_source = True
    smoke = {"created": len(created) == 2, "missing": len(missing) == 1, "attrs": attrs, "values": values, "invalid_source": invalid_source}
    smoke["success"] = all(smoke.values())
    if not smoke["success"]:
        raise AssertionError(smoke)
    print("AIBRIDGE_UI_SMOKE_OK:{0}".format(smoke))
    return smoke
