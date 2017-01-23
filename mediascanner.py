from config import get_config
from database import Database

from formats import FORMATS_GLOB
from formats import glob_match

import os
from time import sleep

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class WatchdogHandler(PatternMatchingEventHandler):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.db = parent.db
        super().__init__(*args, **kwargs)

    def on_created(self, event):
        with self.db.get_session() as session:
            self.db.update_resource_by_path(session, event.src_path)

    def on_modified(self, event):
        with self.db.get_session() as session:
            self.db.update_resource_by_path(session, event.src_path)

    def on_moved(self, event):
        with self.db.get_session() as session:
            r = self.db.get_resource_by_path(session, event.src_path)
            if r is None:
                self.db.update_resource_by_path(session, event.dest_path)
            else:
                r.path = event.dest_path
                session.add(r)


    def on_deleted(self, event):
        with self.db.get_session() as session:
            self.db.remove_resource_by_path(session, event.src_path)


class MediaScanner:
    def __init__(self, paths=None, formats=None):
        self.paths = paths
        self.formats = formats
        self.db = Database()
        self.resources = self.get_resources_in_paths(self.paths)

    def run(self):
        with self.db.get_session() as session:
            self.db.clean_resources(session, self.resources)
            for f in self.resources:
                self.db.update_resource_by_path(session, f)

        observers = {path: Observer() for path in self.paths}
        handler = WatchdogHandler(
            self,
            patterns=FORMATS_GLOB,
            ignore_directories=True
            )
        for path, observer in observers.items():
            observer.schedule(handler, path, recursive=True)
            observer.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            for path, observer in observers.items():
                observer.stop()
                observer.join()

    def get_resources_in_paths(self, paths):
        return [os.path.join(root, f)
                for path in self.paths
                for root, dirs, files in os.walk(path)
                for f in files
                if glob_match(f, FORMATS_GLOB)
                ]


if __name__ == '__main__':
    conf = get_config()

    paths = str(conf['SCANNER']['Path']).split(',')
    formats = str(conf['SCANNER']['Formats']).split(',')

    app = MediaScanner(paths=paths, formats=formats)
    app.run()
