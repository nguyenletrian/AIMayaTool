import unittest

from aimayatool.tools.scene.transfer_attribute import apply_transfer_attributes


class _FakeCmds(object):
    def __init__(self, outgoing):
        self.outgoing = outgoing
        self.add_calls = []

    def objExists(self, name):
        if name.startswith("Target.") and name not in ("Target",):
            return False
        return name in {
            "SourceA.value",
            "SourceB.value",
            "Target",
            "Driven.ty",
        }

    def getAttr(self, plug, lock=False, type=False):
        if lock:
            return plug == "Driven.ty"
        if type:
            return "double"
        return 0.0

    def listConnections(self, plug, s=False, d=False, p=False):
        if d and not s:
            return list(self.outgoing.get(plug, ()))
        return []

    def attributeQuery(self, *args, **kwargs):
        return False

    def addAttr(self, target, **kwargs):
        self.add_calls.append((target, kwargs))


class TransferAttributeRecoveryTests(unittest.TestCase):
    def test_locked_outgoing_destination_fails_before_attribute_creation(self):
        cmds = _FakeCmds({"SourceA.value": ["Driven.ty"]})
        with self.assertRaises(RuntimeError):
            apply_transfer_attributes(
                [{"attribute": "SourceA.value", "target": "Target", "newName": "copiedValue"}],
                cmds_module=cmds,
            )
        self.assertEqual(cmds.add_calls, [])

    def test_later_locked_item_blocks_all_earlier_mutation(self):
        cmds = _FakeCmds({
            "SourceA.value": [],
            "SourceB.value": ["Driven.ty"],
        })
        with self.assertRaises(RuntimeError):
            apply_transfer_attributes(
                [
                    {"attribute": "SourceA.value", "target": "Target", "newName": "copiedA"},
                    {"attribute": "SourceB.value", "target": "Target", "newName": "copiedB"},
                ],
                cmds_module=cmds,
            )
        self.assertEqual(cmds.add_calls, [])


if __name__ == "__main__":
    unittest.main()
