# -*- coding: utf-8 -*-

"""This is a simple python template extension.

This extension should show the API in a comprehensible way. Use the module docstring to provide a \
description of the extension. The docstring should have three paragraphs: A brief description in \
the first line, an optional elaborate description of the plugin, and finally the synopsis of the \
extension.

Synopsis: <trigger> [delay|throw] <query>"""

from albert import *
from pathlib import Path
from unidecode import unidecode
from urllib.parse import urlparse
import os.path

__title__ = "Mate Bookmarks"
__version__ = "0.0.1"
__authors__ = "Pablo Herrero"
__py_deps__ = 'unidecode'

iconPath = iconLookup("folder")
xdg_config_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.join(Path.home(), '.config')

def get_bookmark(url):
    name = url.path.rstrip(os.sep).split(os.sep)[-1]
    return (name, unidecode(name.lower()), f'Open {url.path if url.scheme == "file" else url.geturl()}', url.geturl())

def initialize():
    global bookmarks
    with open(os.path.join(xdg_config_dir, 'gtk-3.0', 'bookmarks'), 'r') as file:
        urls = (urlparse(l) for l in file.read().splitlines())
        bookmarks = [get_bookmark(u) for u in urls if u.scheme != 'file' or u.path != Path.home()]

def handleQuery(query):
    if not query.string:
        return

    query = unidecode(query.string.lower())

    return [ Item(__title__, iconPath, name, text, [ProcAction("Open bookmark", ["xdg-open", url])])
            for name, exp, text, url in bookmarks if (exp.startswith(query)) ]
