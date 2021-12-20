# -*- coding: utf-8 -*-

"""This is a simple python template extension.

This extension should show the API in a comprehensible way. Use the module docstring to provide a \
description of the extension. The docstring should have three paragraphs: A brief description in \
the first line, an optional elaborate description of the plugin, and finally the synopsis of the \
extension.

Synopsis: <trigger> [delay|throw] <query>"""

from albert import *
from pathlib import Path
from urllib.parse import urlparse
import os.path

__title__ = "Mate Bookmarks"
__version__ = "0.0.1"
__authors__ = "Pablo Herrero"

iconPath = iconLookup("folder")

# Can be omitted
def initialize():
    global bookmarks
    with open(os.path.join(Path.home(), '.config', 'gtk-3.0', 'bookmarks'), 'r') as file:
        dirs = (urlparse(l) for l in file.read().splitlines())
        entries = ((d.path.replace(f'{Path.home()}/', ''), d.path) for d in dirs if d.scheme == 'file' and d.path != Path.home())
        bookmarks = [ (n, n.lower() , d) for n, d in entries ]

# Can be omitted
def finalize():
    pass

def handleQuery(query):
    results = []

    for name, exp, path in bookmarks:
        if len(query.string) and exp.startswith(query.string.lower()):
            item = Item(__title__, iconPath, name, f'Open {name} folder', [ProcAction("Open bookmark", ["xdg-open", path])])
            results.append(item)

    return results
