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
from PyQt5 import QtCore
import os.path

__title__ = "Mate Bookmarks"
__version__ = "0.0.1"
__authors__ = "Pablo Herrero"
__py_deps__ = ['unidecode', 'PyQt5']

iconPath = iconLookup("folder")
xdg_config_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.join(Path.home(), '.config')
bookmarks_file = os.path.join(xdg_config_dir, 'gtk-3.0', 'bookmarks')

def get_bookmark(url):
    name = url.path.rstrip(os.sep).split(os.sep)[-1]
    return (name, unidecode(name.lower()), f'Open {url.path if url.scheme == "file" else url.geturl()}', url.geturl())

def update_bookmarks():
    global bookmarks

    if os.path.isfile(bookmarks_file):
        with open(bookmarks_file, 'r') as file:
            urls = (urlparse(l) for l in file.read().splitlines())
            bookmarks = [get_bookmark(u) for u in urls if u.scheme != 'file' or u.path != Path.home()]
    else:
        bookmarks = []

def set_watcher():
    global fs_watcher

    fs_watcher = QtCore.QFileSystemWatcher([bookmarks_file])
    fs_watcher.fileChanged.connect(file_changed)

@QtCore.pyqtSlot(str)
def file_changed(_):
    initialize()

def initialize():
    update_bookmarks()
    set_watcher()

def handleQuery(query):
    if not query.string:
        return

    query = unidecode(query.string.lower())

    return [ Item(__title__, iconPath, name, text, [ProcAction("Open bookmark", ["xdg-open", url])])
            for name, exp, text, url in bookmarks if (exp.startswith(query)) ]
