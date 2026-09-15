from __future__ import absolute_import

from .attributes import create_attribute, normalize_attribute_spec


class _FakeCmds(object):
    def __init__(self):
        self.nodes = {"ctrl"}
        self.attrs = set()
        self.add_calls = []
        self.set_calls = []

    def objExists(self, name):
        return name in self.nodes or name in self.attrs

    def addAttr(self, node, **kwargs):
        self.add_calls.append((node, dict(kwargs)))
        self.attrs.add(node + "." + kwargs["longName"])

    def setAttr(self, plug, *args, **kwargs):
        self.set_calls.append((plug, args, dict(kwargs)))


def run_setup_create_attribute_python_smoke():
    spec = normalize_attribute_spec("mode", "enum", default=1, minimum=0, maximum=2,
                                    enum=["FK", "IK", "Auto"], keyable=False,
                                    lock=True, channel_box=True)
    if spec["enum"] != "FK:IK:Auto": raise RuntimeError("Enum normalization mismatch")
    fake = _FakeCmds()
    plug = create_attribute("ctrl", "mode", "enum", default=1, minimum=0, maximum=2,
                            enum=["FK", "IK", "Auto"], keyable=False, lock=True,
                            channel_box=True, cmds_module=fake)
    if plug != "ctrl.mode": raise RuntimeError("Plug mismatch")
    kwargs = fake.add_calls[0][1]
    if kwargs.get("attributeType") != "enum" or kwargs.get("enumName") != "FK:IK:Auto":
        raise RuntimeError("Enum addAttr arguments mismatch")
    if kwargs.get("defaultValue") != 1 or kwargs.get("minValue") != 0 or kwargs.get("maxValue") != 2:
        raise RuntimeError("Numeric bounds/default mismatch")
    if not fake.set_calls or fake.set_calls[-1][2] != {"lock": True, "channelBox": True, "keyable": False}:
        raise RuntimeError("Post-create state mismatch")
    return "SETUP_CREATE_ATTRIBUTE_PYTHON_SMOKE_OK:1"


RESULT = run_setup_create_attribute_python_smoke()
print(RESULT)
