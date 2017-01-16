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
            # will this work?
            if self.db.get_track_by_uuid(uuid):
                self.uuid = uuid
            else:
                # Track not present in db
                pass

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
    track = Track()
    track.track_number = 3
    track.total_tracks = 20
    track.disc_number = 1
    track.total_discs = 2
    track.title = "Funny Title"
    track.artist = "Happy Artists"
    track.album_artist = "Happy Artists"
    track.date = "20-12-2016"
    track.label = "Greedy records"
    track.isrc = "ASCGM2345"
    track.commit()

    print("Added new track with uuid ", track.uuid)

    db = Database()
    db._drop_tables()
