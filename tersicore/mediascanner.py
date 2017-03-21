import os
from time import sleep

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from tersicore.config import Config
from tersicore.log import get_logger, init_logging
from tersicore.formats import FORMATS_GLOB, glob_match
from tersicore.database import Database, Resource, Track
from tersicore.formats import parse_resource


config = Config()

log = get_logger('mediascanner')
init_logging(config.logging)

db = Database(**config.database)


def get_resource(session, path):
    q = session.query(Resource)
    q = q.filter(Resource.path == path).one_or_none()
    return q


def update_resource(session, path):
    res = get_resource(session, path)
    if res is None:
        res = Resource()
        res.track = Track()
    parse_resource(res, path)
    session.add(res)


def clean_resources(session, paths):
    res = session.query(Resource)\
            .filter(~Resource.path.in_(paths))\
            .all()
    for r in res:
        session.delete(r)


class WatchdogHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        log.debug("Created file (%s) %s",
                  event.event_type, event.src_path)
        with db.get_session() as session:
            update_resource(session, event.src_path)

    def on_modified(self, event):
        log.debug("Modified file (%s) %s",
                  event.event_type, event.src_path)
        with db.get_session() as session:
            update_resource(session, event.src_path)

    def on_moved(self, event):
        log.debug("Moved file (%s) %s -> %s",
                  event.event_type, event.src_path, event.dest_path)

        with db.get_session() as session:
            r = get_resource(session, event.src_path)
            if r is None:
                update_resource(session, event.dest_path)
            else:
                r.path = event.dest_path
                session.add(r)

    def on_deleted(self, event):
        log.debug("Deleted file (%s) %s",
                  event.event_type, event.src_path)
        with db.get_session() as session:
            res = get_resource(session, event.src_path)
            session.delete(res)


class MediaScanner:
    def __init__(self):
        self.paths = config.mediascanner_paths
        self.formats = config.mediascanner_formats
        self.resources = self.get_resources_in_paths(self.paths)

    def run(self):
        with db.get_session() as session:
            clean_resources(session, self.resources)
            for f in self.resources:
                update_resource(session, f)

        observers = {path: Observer() for path in self.paths}

        handler = WatchdogHandler(patterns=FORMATS_GLOB,
                                  ignore_directories=True)

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
