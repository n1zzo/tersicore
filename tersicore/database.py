from contextlib import contextmanager
from uuid import uuid4

import sqlalchemy as sql
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()


def new_uuid():
    return uuid4().hex


class Resource(Base):
    __tablename__ = 'resources'

    uuid = sql.Column(sql.String(32), primary_key=True, default=new_uuid)
    track_uuid = sql.Column(sql.String(32), sql.ForeignKey(
        'tracks.uuid',
        ondelete='CASCADE'
        ), nullable=False)
    path = sql.Column(sql.String(1024), nullable=False)
    codec = sql.Column(sql.String(16), nullable=False)
    sample_rate = sql.Column(sql.Integer, nullable=False)
    bitrate = sql.Column(sql.Integer, nullable=False)

    # Fields to be exposed in the rest API
    def __iter__(self):
        yield 'uuid', self.uuid
        yield 'codec', self.codec
        yield 'sample_rate', self.sample_rate
        yield 'bitrate', self.bitrate


class Track(Base):
    __tablename__ = 'tracks'

    uuid = sql.Column(sql.String(32), primary_key=True, default=new_uuid)
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

    resources = sql.orm.relationship(
        'Resource',
        passive_deletes=True,
        backref=sql.orm.backref(
            'track',
            single_parent=True,
            lazy='joined',
            cascade='save-update, merge, delete, delete-orphan'
            )
        )

    def __iter__(self):
        yield 'uuid', self.uuid
        yield 'track_number', self.track_number
        yield 'total_tracks', self.total_tracks
        yield 'disc_number', self.disc_number
        yield 'total_discs', self.total_discs
        yield 'title', self.title
        yield 'artist', self.artist
        yield 'album_artist', self.album_artist
        yield 'album', self.album
        yield 'compilation', self.compilation
        yield 'date', self.date
        yield 'label', self.label
        yield 'isrc', self.isrc
        yield 'resources', [dict(r) for r in self.resources]


class Database:
    def __init__(self, **kwargs):
        if kwargs['driver'] == 'sqlite':
            eng_str = '{driver}:///{path}'.format(**kwargs)
        else:
            eng_str = '{driver}://{user}:{password}@{host}:{port}/{database}' \
                      '?charset=utf8'.format(**kwargs)

        self.engine = sql.create_engine(eng_str)
        Base.metadata.create_all(self.engine)

        self.make_session = sql.orm.sessionmaker(bind=self.engine,
                                                 expire_on_commit=False)

    @contextmanager
    def get_session(self):
        session = self.make_session()
        try:
            yield session
        except Exception as e:
            print(type(e))
            print(e)
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()
