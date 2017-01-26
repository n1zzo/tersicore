from config import get_config
from formats import parse_resource

import sqlalchemy as sql
import sqlalchemy.ext.declarative

from uuid import uuid4
from contextlib import contextmanager

Base = sqlalchemy.ext.declarative.declarative_base()


def new_uuid():
    return uuid4().hex


class Entry:
    _tables = []

    def __repr__(self):
        return "<{}({})>"\
            .format(self.__class__.__name__, ", ".join([
                "{}='{}'".format(k, v)
                for k, v in self.to_dict().items()
                ]))

    def to_dict(self):
        return {
            k: str(v)
            for k, v in self.__dict__.items()
            if k in self._tables
            }


class Resource(Base, Entry):
    __tablename__ = 'resources'
    _tables = [
        'uuid', 'track_uuid', 'path', 'codec', 'sample_rate', 'bitrate'
        ]

    uuid = sql.Column(sql.String(32), primary_key=True, default=new_uuid)
    track_uuid = sql.Column(sql.String(32), sql.ForeignKey(
        'tracks.uuid',
        ondelete='CASCADE'
        ), nullable=False)
    path = sql.Column(sql.String(1024), nullable=False, unique=True)
    codec = sql.Column(sql.String(16), nullable=False)
    sample_rate = sql.Column(sql.Integer, nullable=False)
    bitrate = sql.Column(sql.Integer, nullable=False)


class Track(Base, Entry):
    __tablename__ = 'tracks'
    _tables = ['uuid', 'track_number', 'total_tracks', 'disc_number',
               'total_discs', 'title', 'artist', 'album_artist',
               'album', 'compilation', 'date', 'label', 'isrc'
               ]

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


class Database:
    Session = None
    engine = None

    def __init__(self):
        config = get_config()
        config_db = config['DATABASE']

        if config_db['Driver'] == 'sqlite':
            eng_str = '{driver}:///{path}'.format(**config_db)
        else:
            eng_str = '{driver}://{user}:{password}@{host}:{port}/{database}'\
                      .format(**config_db)
        self.engine = sql.create_engine(
            eng_str,
            echo=config.getboolean('GENERAL', 'Debug')
            )

        Base.metadata.create_all(self.engine)

        self.Session = sql.orm.sessionmaker(
            bind=self.engine,
            expire_on_commit=False
            )

    @contextmanager
    def get_session(self):
        session = self.Session()
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

    def get_track_by_uuid(self, session, uuid):
        q = session.query(Track)\
            .join(Resource)\
            .filter(Track.uuid == uuid)\
            .one_or_none()
        return q

    def get_resource_by_path(self, session, path):
        q = session.query(Resource)\
            .filter(Resource.path == path)\
            .one_or_none()
        return q

    def update_resource_by_path(self, session, path):
        res = self.get_resource_by_path(session, path)
        if res is None:
            res = Resource()
            res.track = Track()
        parse_resource(res, path)
        session.add(res)

    def remove_track_by_uuid(self, session, uuid):
        session.query(Track)\
            .filter(Track.uuid == uuid)\
            .delete(synchronize_session=False)

    def remove_resource_by_path(self, session, path):
        session.query(Resource)\
            .filter(Resource.path == path)\
            .delete(synchronize_session=False)

    def clean_resources(self, session, paths):
        session.query(Resource)\
            .filter(~Resource.path.in_(paths))\
            .delete(synchronize_session=False)

    def get_tracks(self, session, filters):
        if filters is None:
            q = session.query(Track)\
                .join(Resource)\
                .all()
        else:
            q = session.query(Track)\
                .join(Resource)\
                .filter(sql.or_(
                    Track.title.like(filters['text']),
                    Track.artist.like(filters['text']),
                    Track.album.like(filters['text'])
                    )
                ).all()
        return q
