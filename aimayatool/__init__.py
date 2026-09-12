from __future__ import absolute_import

__version__ = "0.1.0"


def launch():
    from .app import launch as _launch
    return _launch()
