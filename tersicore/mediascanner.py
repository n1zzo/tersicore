import os
from time import sleep

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from tersicore.log import get_logger

from tersicore.formats import FORMATS_GLOB
from tersicore.formats import glob_match

from tersicore.database import Resource, Track
from tersicore.formats import parse_resource

import argparse
from tersicore.config import Config
from tersicore.log import init_logging
from tersicore.database import Database


log = get_logger('mediascanner')


def get_resource_by_path(session, path, join=False):
    q = session.query(Resource)
    if join is True:
        q = q.join(Track)
    q = q.filter(Resource.path == path).one_or_none()
    return q


def update_resource_by_path(session, path):
    res = get_resource_by_path(session, path)
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
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.db = parent.db
        super().__init__(*args, **kwargs)

    def on_created(self, event):
        log.debug("Created file (%s) %s",
                  event.event_type, event.src_path)
        with self.db.get_session() as session:
            update_resource_by_path(session, event.src_path)

    def on_modified(self, event):
        log.debug("Modified file (%s) %s",
                  event.event_type, event.src_path)
        with self.db.get_session() as session:
            update_resource_by_path(session, event.src_path)

    def on_moved(self, event):
        log.debug("Moved file (%s) %s -> %s",
                  event.event_type, event.src_path, event.dest_path)
        with self.db.get_session() as session:
            r = get_resource_by_path(session, event.src_path)
            if r is None:
                update_resource_by_path(session, event.dest_path)
            else:
                r.path = event.dest_path
                session.add(r)

    def on_deleted(self, event):
        log.debug("Deleted file (%s) %s",
                  event.event_type, event.src_path)
        with self.db.get_session() as session:
            res = get_resource_by_path(session, event.src_path)
            session.delete(res)


class MediaScanner:
    def __init__(self, paths, formats, database):
        self.paths = paths
        self.formats = formats
        self.resources = self.get_resources_in_paths(self.paths)
        self.db = database

    def run(self):
        with self.db.get_session() as session:
            clean_resources(session, self.resources)
            for f in self.resources:
                update_resource_by_path(session, f)

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


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--config-dir')
    parser.add_argument('--tersicore-config')
    parser.add_argument('--logging-config')

    args = parser.parse_args()

    config = Config(
        basedir=args.config_dir,
        tersicore_file=args.tersicore_config,
        logging_file=args.logging_config)

    config_logging = config.logging
    init_logging(config_logging)

    config_database = config.tersicore['DATABASE']
    database = Database(**config_database)

    config_scanner = config.tersicore['SCANNER']
    config_mediascanner_paths = str(config_scanner['Path']).split(',')
    config_mediascanner_formats = str(config_scanner['Formats']).split(',')

    mediascanner = MediaScanner(
        paths=config_mediascanner_paths,
        formats=config_mediascanner_formats,
        database=database)

    mediascanner.run()
