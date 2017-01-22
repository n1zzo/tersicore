from config import get_config
from database import Database

import os
from time import sleep
from datetime import date
from fnmatch import fnmatch

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import mutagen
import mutagen.oggvorbis
import mutagen.id3


FORMATS = {
    mutagen.id3.ID3FileType: {
        'pretty_name': 'mp3',
        'extensions': ['mp3']
        },
    mutagen.oggvorbis.OggVorbis: {
        'pretty_name': 'ogg_vorbis',
        'extensions': ['ogg', 'oga']
        }
    }

FORMATS_GLOB = ["*.{}".format(ext)
                for k, v in FORMATS.items()
                for ext in v['extensions']
                ]


def glob_match(path, globs):
    return any(fnmatch(path, glob) for glob in globs)


class MediaScanner:
    class WatchdogHandler(PatternMatchingEventHandler):
        def __init__(self, parent, *args, **kwargs):
            self.parent = parent
            self.db = parent.db
            super().__init__(*args, **kwargs)

        def on_any_event(self, event):
            with self.db.get_session() as session:
                self.parent.add_update_resource(session, event.src_path)

    def __init__(self, paths=None, formats=None):
        self.paths = paths
        self.formats = formats
        self.db = Database()

    def run(self):
        with self.db.get_session() as session:
            self.clean_database(session)
            for f in self.get_resources_in_fs():
                self.add_update_resource(session, f)

        observers = {path: Observer() for path in self.paths}
        handler = self.WatchdogHandler(
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

    def get_resources_in_fs(self):
        return [os.path.join(root, f)
                for path in self.paths
                for root, dirs, files in os.walk(path)
                for f in files
                if glob_match(f, FORMATS_GLOB)
                ]

    def get_resource_by_path(self, session, path):
        q = session.query(self.db.Resource)\
            .filter(self.db.Resource.path == path).one_or_none()
        return q

    def clean_database(self, session):
        session.query(self.db.Resource)\
            .filter(~self.db.Resource.path.in_(self.get_resources_in_fs()))\
            .delete(synchronize_session=False)

    def add_update_resource(self, session, path):
        res = self.get_resource_by_path(session, path)
        if res is None:
            res = self.db.Resource()
            res.track = self.db.Track()

        media = mutagen.File(path)

        res.path = path
        res.path = path
        res.codec = FORMATS[type(media)]['pretty_name']
        res.bitrate = media.info.bitrate

        res.track.track_number = media.tags['tracknumber']
        res.track.total_tracks = media.tags['totaltracks']
        res.track.disc_number = media.tags['discnumber']
        res.track.total_discs = media.tags['totaldiscs']
        res.track.title = media.tags['title']
        res.track.artist = media.tags['artist']
        res.track.album_artist = media.tags['ensemble']
        res.track.album = media.tags['album']
        res.track.compilation = False
        res.track.date = date(int(media.tags['date'][0]), 1, 1)
        res.track.label = media.tags['organization']
        res.track.isrc = media.tags['isrc']

        session.add(res)


if __name__ == '__main__':
    conf = get_config()

    paths = str(conf['SCANNER']['Path']).split(',')
    formats = str(conf['SCANNER']['Formats']).split(',')

    app = MediaScanner(paths=paths, formats=formats)
    app.run()
