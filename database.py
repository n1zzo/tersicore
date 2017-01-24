from config import get_config
from formats import parse_resource

import sqlalchemy as sql
import sqlalchemy.ext.declarative

from uuid import uuid4
from contextlib import contextmanager


def new_uuid():
    return uuid4().hex


class Database:
    Base = sqlalchemy.ext.declarative.declarative_base()
    Session = None
    engine = None

    class Resource(Base):
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

        def __repr__(self):
            return "<{}({})>"\
                .format(self.__class__.__name__, ", ".join([
                    "{}='{}'".format(k, v)
                    for k, v in self.dict().items()
                    ]))

        def dict(self):
            return {
                k: str(v)
                for k, v in self.__dict__.items()
                if k in self._tables
                }

    class Track(Base):
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
                cascade='save-update,  merge, delete, delete-orphan'
                )
            )

        def __repr__(self):
            return "<{}({})>"\
                .format(self.__class__.__name__, ", ".join([
                    "{}='{}'".format(k, v)
                    for k, v in self.dict().items()
                    ]))

        def dict(self):
            return {
                k: str(v)
                for k, v in self.__dict__.items()
                if k in self._tables
                }

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
        except Exception as e:
            print(e)
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    def get_resource_by_path(self, session, path):
        q = session.query(self.Resource)\
            .filter(self.Resource.path == path).one_or_none()
        return q

    def update_resource_by_path(self, session, path):
        res = self.get_resource_by_path(session, path)
        if res is None:
            res = self.Resource()
            res.track = self.Track()
        parse_resource(res, path)
        session.add(res)

    def remove_resource_by_path(self, session, path):
        session.query(self.Resource)\
            .filter(self.Resource.path == path)\
            .delete(synchronize_session=False)

    def clean_resources(self, session, paths):
        session.query(self.Resource)\
            .filter(~self.Resource.path.in_(paths))\
            .delete(synchronize_session=False)

    def get_tracks(self, session, filters):
        if filters is None:
            q = session.query(self.Track)\
                .join(self.Resource)\
                .all()
        else:
            q = session.query(self.Track)\
                .join(self.Resource)\
                .filter(sql.or_(
                    self.Track.title.like(filters['text']),
                    self.Track.artist.like(filters['text']),
                    self.Track.album.like(filters['text'])
                    )
                ).all()

        return q


if __name__ == '__main__':
    # TODO: real tests
    from test import test_database
    test_database()
