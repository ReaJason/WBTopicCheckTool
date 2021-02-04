import os
import sys

__all__ = [
    "ICON_PATH",
    "ROOT_PATH"
]

ROOT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
RES_PATH = os.path.join(ROOT_PATH, 'res')
ICON_PATH = os.path.join(RES_PATH, "icon.png")