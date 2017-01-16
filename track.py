from database import Database


class Track:
    uuid = None
    track_number = None
    total_tracks = None
    disc_number = None
    total_discs = None
    title = None
    artist = None
    album_artist = None
    album = None
    date = None
    label = None
    isrc = None

    db = None

    def __init__(self, uuid=None):
        self.db = Database()

        if uuid:
            track = self.db.get_track_by_uuid(uuid)
            if track:
                self._load_tags(track)
            else:
                # Track not present in db
                pass

    def _load_tags(self, track):
        self.uuid = track.uuid
        self.track_number = track.track_number
        self.total_tracks = track.total_tracks
        self.disc_number = track.disc_number
        self.total_discs = track.total_discs
        self.title = track.title
        self.artist = track.artist
        self.album_artist = track.album_artist
        self.album = track.album
        self.date = track.date
        self.label = track.label
        self.isrc = track.isrc

    def commit(self):
        track = self.db.Track(
                uuid=self.uuid,
                track_number=self.track_number,
                total_tracks=self.total_tracks,
                disc_number=self.disc_number,
                total_discs=self.total_discs,
                title=self.title,
                artist=self.artist,
                album_artist=self.album_artist,
                album=self.album,
                date=self.date,
                label=self.label,
                isrc=self.isrc)

        if self.uuid is None:
            self.uuid = self.db.add_track(track)
        else:
            self.db.update_track(track)

# TODO: why is this blowing db.add_track()? Asking the python gurus
#    def __setattr__(self, name, value):
#        if name is 'uuid':
#            # TODO: check if uuid is present in db
#            self.__dict__[name] = value


if __name__ == '__main__':
    track1 = Track()
    track1.track_number = 3
    track1.total_tracks = 20
    track1.disc_number = 1
    track1.total_discs = 2
    track1.title = "Funny Title"
    track1.artist = "Happy Artists"
    track1.album_artist = "Happy Artists"
    track1.date = "20-12-2016"
    track1.label = "Greedy records"
    track1.isrc = "ASCGM2345"
    track1.commit()

    print("Added new track with uuid", track1.uuid)

    track2 = Track(track1.uuid)
    print("New track has the following values:",
            track2.uuid, track2.track_number, track2.total_tracks,
            track2.disc_number, track2.total_discs, track2.title, track2.artist,
            track2.album_artist, track2.date, track2.label, track2.isrc)

    #db = Database()
    #db._drop_tables()
