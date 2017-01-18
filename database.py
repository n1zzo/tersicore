from contextlib import contextmanager
from uuid import uuid4

import sqlalchemy as sql
import sqlalchemy.ext.declarative
import sqlalchemy.orm

from config import get_config


class Database(object):
    Base = sql.ext.declarative.declarative_base()
    Session = None
    engine = None

    class Track(Base):
        def _new_uuid(self):
            return uuid4().hex

        __tablename__ = 'tracks'

        uuid = sql.Column(sql.String(32), primary_key=True, default=_new_uuid)
        track_number = sql.Column(sql.Integer)
        total_tracks = sql.Column(sql.Integer)
        disc_number = sql.Column(sql.Integer)
        total_discs = sql.Column(sql.Integer)
        title = sql.Column(sql.String(256))
        artist = sql.Column(sql.String(256))
        album_artist = sql.Column(sql.String(256))
        album = sql.Column(sql.String(256))
        compilation = sql.Column(sql.Boolean)
        date = sql.Column(sql.Date)
        label = sql.Column(sql.String(256))
        isrc = sql.Column(sql.String(256))

        def __repr__(self):
            return (
                "<Track(uuid='%s', "
                "track_number='%s', total_tracks='%s', "
                "disc_number='%s', total_discs='%s', "
                "title='%s', artist='%s', album_artist='%s', album='%s', "
                "date='%s', label='%s', isrc='%s')>" % (
                    self.uuid,
                    self.track_number, self.total_tracks,
                    self.disc_number, self.total_discs,
                    self.title, self.artist, self.album_artist, self.album,
                    self.date, self.label, self.isrc
                    )
                )

    def __init__(self):
        config = get_config()

        engine_str = "{driver}://{user}:{password}@{host}:{port}/{database}"\
                .format(
                    driver=config['DATABASE']['Driver'],
                    user=config['DATABASE']['User'],
                    password=config['DATABASE']['Password'],
                    host=config['DATABASE']['Host'],
                    port=config['DATABASE']['Port'],
                    database=config['DATABASE']['Database']
                    )
        self.engine = sql.create_engine(
            engine_str,
            echo=config.getboolean('GENERAL', 'Debug')
            )

        self.Base.metadata.create_all(self.engine)

        self.Session = sql.orm.sessionmaker(
            bind=self.engine,
            expire_on_commit=False
            )

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
        except:
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

if __name__ == '__main__':
    db = Database()

    track1 = db.Track(
            track_number=1,
            total_tracks=2,
            disc_number=1,
            total_discs=1,
            title='Mr Happy mispelled',
            artist='DJ Hazard; Distorted Minds',
            album_artist='DJ Hazard; Distorted Minds',
            album='Mr Happy / Super Drunk',
            compilation=False,
            date='2007-10-08',
            label='Playaz Recordings',
            isrc='PLAYAZ002'
            )

    track2 = db.Track(
            track_number=2,
            total_tracks=2,
            disc_number=1,
            total_discs=1,
            title='Super Drunk',
            artist='DJ Hazard; Distorted Minds',
            album_artist='DJ Hazard; Distorted Minds',
            album='Mr Happy / Super Drunk',
            compilation=False,
            date='2007-10-08',
            label='Playaz Recordings',
            isrc='PLAYAZ002'
            )

    with db.get_session() as session:
        session.add(track1)
        session.add(track2)
        print(track1, track2)

    with db.get_session() as session:
        session.add(track1)
        track1.title = 'Mr Happy'
        print(track1)

    print(track1, track2)
