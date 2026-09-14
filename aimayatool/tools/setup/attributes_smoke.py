from __future__ import absolute_import
import importlib
import maya.cmds as cmds
from . import attributes as attributes_module


def _attributes(): return importlib.reload(attributes_module)


def run_setup_attribute_copy_smoke():
    attributes = _attributes(); cmds.file(new=True, force=True)
    source = cmds.createNode("transform", name="attrSource")
    target_a = cmds.createNode("transform", name="attrTargetA")
    target_b = cmds.createNode("transform", name="attrTargetB")
    cmds.setAttr(source + ".tx", 7.5); cmds.setAttr(target_a + ".tx", 0.0); cmds.setAttr(target_b + ".tx", -3.0)
    attributes.copy_attribute_value(source, [target_a, target_b], "tx")
    if abs(cmds.getAttr(target_a + ".tx") - 7.5) > 1e-6: raise RuntimeError("Target A attribute mismatch.")
    if abs(cmds.getAttr(target_b + ".tx") - 7.5) > 1e-6: raise RuntimeError("Target B attribute mismatch.")
    return "SETUP_ATTRIBUTE_COPY_SMOKE_OK:2"
