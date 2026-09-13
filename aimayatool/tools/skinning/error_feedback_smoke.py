from __future__ import absolute_import

import importlib

from aimayatool.tools import skinning


class _FakeCmds(object):
    def __init__(self):
        self.warnings = []
        self.messages = []

    def warning(self, message):
        self.warnings.append(message)

    def inViewMessage(self, **kwargs):
        self.messages.append(kwargs)


def run_error_feedback_smoke():
    importlib.reload(skinning)
    fake = _FakeCmds()
    original_cmds = skinning._cmds
    original_traceback = skinning.traceback.print_exc
    traces = []
    try:
        skinning._cmds = lambda: fake
        skinning.traceback.print_exc = lambda: traces.append(True)

        def fail():
            raise RuntimeError('Select source mesh first')

        result = skinning._run('Copy Skin', fail)
        if result is not None:
            raise RuntimeError('failed UI callback should return None')
        if len(fake.warnings) != 1 or 'Copy Skin failed: Select source mesh first' not in fake.warnings[0]:
            raise RuntimeError('warning is not operation-specific: %s' % fake.warnings)
        if len(fake.messages) != 1 or 'Copy Skin failed: Select source mesh first' not in fake.messages[0].get('amg', ''):
            raise RuntimeError('in-view error is not operation-specific: %s' % fake.messages)
        if len(traces) != 1:
            raise RuntimeError('unexpected error traceback was not surfaced exactly once')
        return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_ACTIONABLE_ERROR_FEEDBACK_OK'
    finally:
        skinning._cmds = original_cmds
        skinning.traceback.print_exc = original_traceback
