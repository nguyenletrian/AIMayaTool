from __future__ import print_function

import os
import sys


def _repo_root():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


def install_and_launch():
    root = _repo_root()
    if root not in sys.path:
        sys.path.insert(0, root)

    import aimayatool
    return aimayatool.launch()


def onMayaDroppedPythonFile(*_args, **_kwargs):
    return install_and_launch()


if __name__ == "__main__":
    install_and_launch()
