from config import get_config
# from database import Database

import os
from time import sleep
from fnmatch import fnmatch
import logging as log

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

log.basicConfig(filename='scanner.log', level=log.DEBUG)


def add_resource(path):
    log.debug('Adding {}'.format(path))


def update_resource(path):
    log.debug('Updating {}'.format(path))


def remove_resource(path):
    log.debug('Removing {}'.format(path))


class Handler(PatternMatchingEventHandler):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def on_any_event(self, event):
        update_resource(event.src_path)


class Scanner(Observer):
    def __init__(self, db, path, patterns):
        super().__init__()

        self.patterns = patterns
        self.path = path

        handler = Handler(db, patterns=patterns, ignore_directories=True)
        self.schedule(handler, path, recursive=True)

    def start(self):
        self.force_scan()
        super().start()

    def force_scan(self):

        def match(f):
            return any(fnmatch(f, pattern)
                       for pattern in self.patterns)

        matches = [os.path.join(root, f)
                   for root, dirs, files in os.walk(path)
                   for f in files
                   if match(f)]

        for file_name in matches:
            add_resource(file_name)


if __name__ == "__main__":
    log.debug('Starting scanner')

    conf = get_config()
    path = conf["SCANNER"]["path"]

    log.debug('Initializing db connection')
    # db = Database()
    db = None

    scanner = Scanner(db, path, ["*.mp3", "*.flac", "*.ogg"])
    scanner.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        scanner.stop()
    scanner.join()
