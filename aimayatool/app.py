from __future__ import absolute_import


def launch():
    try:
        from .ui.main_window import show
    except ImportError as exc:
        raise RuntimeError("AIMayaTool must be launched inside Maya: {}".format(exc))
    return show()
