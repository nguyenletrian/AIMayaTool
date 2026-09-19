from __future__ import absolute_import

from .components import button_row


def run():
    try:
        button_row([])
        raise AssertionError("empty button row unexpectedly accepted")
    except ValueError:
        pass
    return "UI_COMPONENTS_PYTHON_CONTRACT_OK"


RESULT = run()
assert RESULT == "UI_COMPONENTS_PYTHON_CONTRACT_OK"
