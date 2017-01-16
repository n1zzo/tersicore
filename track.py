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
    date = None
    label = None
    isrc = None

    db = None

    def __init__(self, uuid=None):
        self.db = Database()

        if uuid is not None:
            # TODO: check if uuid is present in db
            self.uuid = uuid

    def commit(self):
        if self.uuid is None:
            self.uuid = self.db.add_track(
                    self.track_number, self.total_tracks,
                    self.disc_number, self.total_discs,
                    self.title, self.artist, self.album_artist,
                    self.date, self.label, self.isrc)
        else:
            self.db.update_track(self.uuid,
                    self.track_number, self.total_tracks,
                    self.disc_number, self.total_discs,
                    self.title, self.artist, self.album_artist,
                    self.date, self.label, self.isrc)

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
