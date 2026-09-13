from __future__ import absolute_import

from . import proxy_skin


_SNAPSHOT = None


def has_snapshot():
    return _SNAPSHOT is not None


def clear_snapshot():
    global _SNAPSHOT
    _SNAPSHOT = None
    return True


def copy_from_selection():
    """Capture the current proxy source selection for later interactive paste."""
    global _SNAPSHOT
    _SNAPSHOT = proxy_skin.capture_proxy_snapshot_from_selection()
    return dict(_SNAPSHOT)


def paste_to_selection(surface_association='closestPoint'):
    """Paste the current interactive proxy snapshot to selected targets."""
    if _SNAPSHOT is None:
        raise RuntimeError('Copy proxy skin before pasting')
    return proxy_skin.paste_proxy_snapshot_to_selection(_SNAPSHOT, surface_association=surface_association)
