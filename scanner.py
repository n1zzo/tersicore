from config import get_config
from database import Database

import os
import logging as log
from time import sleep
from fnmatch import fnmatch
from datetime import date

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from mutagen import File

log.basicConfig(filename='scanner.log', level=log.DEBUG)


def add_resource(db, path):
    log.debug('Adding {}'.format(path))
    tag = File(path)

    track = db.Track(
        track_number=tag["tracknumber"],
        total_tracks=tag["totaltracks"],
        disc_number=tag["discnumber"],
        total_discs=tag["totaldiscs"],
        title=tag["title"],
        artist=tag["artist"],
        album_artist=tag["ensemble"],
        album=tag["album"],
        compilation=False,
        date=date(tag["date"]),
        label=tag["organization"],
        isrc=tag["isrc"]
        )

    with db.get_session() as session:
        session.add(track)
        track.resources = [
            db.Resource(codec=getCodec(type(tag)),
                        bitrate=tag.info.bitrate,
                        path=path),
        ]


def getCodec(filetype):
    pass


def update_resource(db, path):
    log.debug('Updating {}'.format(path))


def remove_resource(db, path):
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

        self.db = db
        self.path = path
        self.patterns = patterns

        handler = Handler(db, patterns=patterns, ignore_directories=True)
        self.schedule(handler, path, recursive=True)

    def start(self):
        self.check_consistency()
        super().start()

    def check_consistency(self):
        def match(f):
            return any(fnmatch(f, pattern)
                       for pattern in self.patterns)

        matches = [os.path.join(root, f)
                   for root, dirs, files in os.walk(path)
                   for f in files
                   if match(f)]

        db = self.db
        with db.get_session() as session:
            for res in session.query(db.Resource)\
                    .filter(~db.Resource.path.in_(matches)).all():
                session.delete(res)
                log.debug('Removing {}'.format(res))

        for file_name in matches:
            add_resource(db, file_name)


if __name__ == "__main__":
    log.debug('Starting scanner')

    conf = get_config()
    path = conf["SCANNER"]["path"]

    log.debug('Initializing db connection')
    db = Database()

    scanner = Scanner(db, path, ["*.mp3", "*.flac", "*.ogg"])
    scanner.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        scanner.stop()
    scanner.join()
