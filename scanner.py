from config import get_config
from database import Database

import os
import logging as log
from time import sleep
from fnmatch import fnmatch
from datetime import date

import mutagen
import mutagen.oggvorbis
import mutagen.flac
import mutagen.id3

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

log.basicConfig(filename='scanner.log', level=log.DEBUG)

CODECS = {
        mutagen.id3.ID3FileType: "mp3",
        mutagen.flac.FLAC: "flac",
        mutagen.oggvorbis.OggVorbis: "ogg vorbis"
        }


def add_resource(db, path):
    log.debug("Looking for {} in db...".format(path))

    with db.get_session() as session:
        try:
            q = session.query(db.Resource)\
                .filter(db.Resource.path == path).one()
        except:
            return
        else:
            pass

    tags = mutagen.File(path)

    track = db.Track(
        track_number=tags["tracknumber"],
        total_tracks=tags["totaltracks"],
        disc_number=tags["discnumber"],
        total_discs=tags["totaldiscs"],
        title=tags["title"],
        artist=tags["artist"],
        album_artist=tags["ensemble"],
        album=tags["album"],
        compilation=False,
        date=date(int(tags['date'][0]), 1, 1),
        label=tags["organization"],
        isrc=tags["isrc"]
        )
    track.resources = [
        db.Resource(codec=CODECS[type(tags)],
                    bitrate=tags.info.bitrate,
                    path=path)
        ]

    with db.get_session() as session:
        session.add(track)

    # TESTING
    print("Dump:")                                                         
    q = session.query(db.Track, db.Resource).join(db.Resource).all()        
    print(q)


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
