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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
import os.path

md_iid = "5.0"
md_version = "0.3"
md_name = "Mate Bookmarks"
md_description = "Launch Bookmarks from Caja"
md_lib_dependencies = ['watchdog']
md_license = "MIT"
md_url = "https://github.com/pabloh/mate_bookmarks"
md_authors = ["@pabloh"]

class Plugin(PluginInstance, GlobalQueryHandler):
    xdg_config_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.join(Path.home(), '.config')
    bookmarks_file = os.path.join(xdg_config_dir, 'gtk-3.0', 'bookmarks')

    def __del__(self):
        if hasattr(self, 'observer'):
            self.observer.stop_watching()

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(self)
        # GlobalQueryHandler.__init__(self, md_id, md_name, md_description, defaultTrigger=md_id)
        self.update_bookmarks()
        self.observer = BookmarkWatcher.start_watching_on_bg(self)

    def rankItems(self, context):
        exp_query = context.query.strip().lower()
        return [
            RankItem(
                item=StandardItem(
                    id=exp,
                    text=text,
                    subtext=subtext,
                    icon_factory=lambda: Icon.theme("folder"),
                    actions=[Action("open", "Open bookmark", lambda url=url: runDetachedProcess(["xdg-open", url]))]),
                score=0.0 if not exp_query else len(exp_query) / len(exp))
            for text, exp, subtext, url in self.bookmarks if (exp.startswith(exp_query))
        ]

    def get_bookmark(self, url):
        dirname = url.path.rstrip(os.sep).split(os.sep)[-1]
        return (dirname, dirname.lower(), f'Open {url.path if url.scheme == "file" else url.geturl()}', url.geturl())

    def update_bookmarks(self):
        # info('Updating bookmarks')
        if os.path.isfile(self.bookmarks_file):
            with open(self.bookmarks_file, 'r') as file:
                urls = (urlparse(l) for l in file.read().splitlines())
                self.bookmarks = [self.get_bookmark(u) for u in urls if u.scheme != 'file' or u.path != Path.home()]
        else:
            self.bookmarks = []

class BookmarkWatcher(FileSystemEventHandler):
    def __init__(self, plugin):
        self.plugin = plugin
        self.bookmarks_file = plugin.bookmarks_file
        self.observer = Observer()
        self.observer.schedule(self, os.path.dirname(self.bookmarks_file), recursive=False)

    @classmethod
    def start_watching_on_bg(cls, plugin):
        bw = cls(plugin)
        bw.start_watching()
        return bw

    def start_watching(self):
        self.thread = Thread(target=self.observer.start)
        self.thread.start()

    def stop_watching(self):
        self.observer.stop()
        self.thread.join()

    def on_deleted(self, event): self.on_modified(event)

    def on_modified(self, event):
        if event.src_path.endswith(self.bookmarks_file):
            self.plugin.update_bookmarks()
