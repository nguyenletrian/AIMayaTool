from __future__ import absolute_import

import unittest
from .create_attribute import build_attribute_spec, create_attribute


class FakeCmds(object):
    def __init__(self, nodes=(), plugs=()): self.nodes, self.plugs = set(nodes), set(plugs)
    def objExists(self, name): return name in self.nodes or name in self.plugs


class CreateAttributeTests(unittest.TestCase):
    def _create(self, nodes, plugs=()):
        calls, cmds = [], FakeCmds(nodes, plugs)
        def fake(node, attr, **kwargs): calls.append((node, attr, kwargs)); return node + "." + attr
        return cmds, calls, fake

    def test_numeric(self):
        cmds, calls, fake = self._create(("A",))
        result = create_attribute("A", "weight", "double", True, False, True, 0, 1, .5,
                                  cmds_module=cmds, create_attribute_fn=fake)
        self.assertEqual(result[0]["status"], "created")
        self.assertEqual(calls[0][2]["minimum"], 0.0); self.assertEqual(calls[0][2]["default"], .5)

    def test_enum(self):
        cmds, calls, fake = self._create(("A",))
        create_attribute(["A"], "mode", "enum", False, True, True, 0, 2, 1, "FK:IK:Auto",
                         cmds_module=cmds, create_attribute_fn=fake)
        self.assertEqual(calls[0][2]["enum"], "FK:IK:Auto")

    def test_string_and_matrix_are_data_specs(self):
        string_spec = build_attribute_spec("label", "string", default="hello", minimum=1, maximum=2, enum="X:Y")
        matrix_spec = build_attribute_spec("bind", "matrix", default=3, minimum=1, maximum=2)
        self.assertEqual(string_spec["default"], "hello"); self.assertIsNone(string_spec["minimum"])
        self.assertIsNone(matrix_spec["default"]); self.assertIsNone(matrix_spec["maximum"])

    def test_missing_object_skips_without_create(self):
        cmds, calls, fake = self._create(())
        result = create_attribute(["Missing"], "x", cmds_module=cmds, create_attribute_fn=fake)
        self.assertEqual(result[0]["status"], "skipped_missing_object"); self.assertEqual(calls, [])

    def test_existing_attribute_skips_without_create(self):
        cmds, calls, fake = self._create(("A",), ("A.x",))
        result = create_attribute(["A"], "x", cmds_module=cmds, create_attribute_fn=fake)
        self.assertEqual(result[0]["status"], "skipped_existing_attribute"); self.assertEqual(calls, [])


def run_scene_create_attribute_python_smoke():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CreateAttributeTests)
    result = unittest.TestResult(); suite.run(result)
    if not result.wasSuccessful(): raise RuntimeError("CreateAttribute Python smoke failed: {0} {1}".format(result.failures, result.errors))
    return "SCENE_CREATE_ATTRIBUTE_PYTHON_SMOKE_OK:{0}".format(result.testsRun)


RESULT = run_scene_create_attribute_python_smoke()
print(RESULT)
