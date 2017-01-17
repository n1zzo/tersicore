import sqlalchemy as sql
import uuid
from config import get_config


def create_table_tracks(engine, metadata):
    tracks = sql.Table(
        "tracks", metadata,
        sql.Column("UUID", sql.String(16), nullable=False,
                   primary_key=True),
        sql.Column("track_number", sql.Integer),
        sql.Column("total_tracks", sql.Integer),
        sql.Column("disc_number",  sql.Integer),
        sql.Column("total_disks",  sql.Integer),
        sql.Column("title",        sql.String(256), nullable=False),
        sql.Column("artist",       sql.String(256), nullable=False),
        sql.Column("album_artist", sql.String(256)),
        sql.Column("date",         sql.String(256)),
        sql.Column("label",        sql.String(256)),
        sql.Column("ISRC",         sql.String(256)))
    tracks.create(engine, checkfirst=True)
    return tracks


class Database:
    def __init__(self):
        conf = get_config()
        db_conf = conf["DATABASE"]
        db_url = "mysql+pymysql://{user}:{password}@{host}:{port}"\
                 .format(**db_conf)

        self.engine = sql.create_engine(db_url)

        db_name = db_conf["database"]
        self.engine.execute("CREATE DATABASE IF NOT EXISTS {};"
                            .format(db_name))
        self.engine.execute("USE {};".format(db_name))

        self.metadata = sql.MetaData()
        self.tracks = create_table_tracks(self.engine, self.metadata)

    def drop_tables(self):
        self.metadata.drop_all(self.engine)

    def add_track(self, tag):
        UUID = uuid.uuid4().hex[:16]  # FIXME: field size too small
        ins = self.tracks.insert().values(UUID=UUID, **tag)
        self.engine.execute(ins)
        return UUID

    def update_track(self, UUID, tag):
        # FIXME: not tested
        upd = self.tracks.update().values(UUID=UUID, **tag)
        self.engine.execute(upd)


if __name__ == "__main__":
    db = Database()

    test_tag = {
        "track_number": 3,
        "total_tracks": 20,
        "disc_number": 2,
        "total_disks": 1,
        "title": "Funny Title",
        "artist": "Happy Artists",
        "album_artist": "Happy Artists Collection",
        "date": "20-12-2016",
        "label": "Greedy Records",
        "ISRC": "ASCGM2345"}

    track_id = db.add_track(test_tag)
    print("Inserted new track with UUID", str(track_id))

    test_tag["title"] = "NEWTITLE"
    db.update_track(track_id, test_tag)

    db.drop_tables()
