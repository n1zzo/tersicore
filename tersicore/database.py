from contextlib import contextmanager
from uuid import uuid4
from datetime import date

import sqlalchemy as sql
import sqlalchemy.ext.declarative

from tersicore.formats import parse_resource

Base = sqlalchemy.ext.declarative.declarative_base()


def new_uuid():
    return uuid4().hex


class Entry:
    def __repr__(self):
        return "<{}({})>"\
            .format(self.__class__.__name__, ", ".join([
                "{}='{}'".format(k, v)
                for k, v in self.dict()
                ]))

    def dict(self):
        d = {}
        # Step #1
        # Build the new dictionary with strings, integers and dates taken from
        # self class attributes.
        for k, v in self.__dict__.items():
            if isinstance(v, (str, int, date)):
                d[k] = v
        # Step #2
        # Since, for example, Track has no explicit resources attribute because
        # it is backreferenced from Resource we need a little workaround to
        # make sure all relationships are caught.
        # __mapper__.relationships is a list of tuple where the first element
        # of the tuple is the name of the relationship.
        relationships = self.__mapper__.relationships.keys()
        for r in relationships:
            rel = getattr(self, r)
            # If the relationship points to multiple rows we run .dict() again
            # for each element and add this new list to the dictionary
            if isinstance(rel, list):
                d[r] = [e.dict() for e in rel]
        return d


class Resource(Base, Entry):
    __tablename__ = 'resources'

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

    def __init__(self, **kwargs):

        if kwargs['driver'] == 'sqlite':
            eng_str = '{driver}:///{path}'.format(**kwargs)
        else:
            eng_str = '{driver}://{user}:{password}@{host}:{port}/{database}'\
                      .format(**kwargs)
        self.engine = sql.create_engine(eng_str)

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

    def get_tracks(self, session, join=False, one=False, **kwargs):
        q = session.query(Track)
        filters_or = [
            getattr(Track, c).like("%{}%".format(kwargs['text']))
            for c in Track.__dict__
            # TODO
            # Here we are matching only for strings.
            # We need a more solid logic.
            if type(getattr(Track, c)) is str
            if 'text' in kwargs
            ]
        filters_and = [
            getattr(Track, k).like("%{}%".format(v))
            for k, v in kwargs.items()
            # TODO
            # Here we don't check if kwargs are in Track.dict() since it is not
            # a static method. Can it be?
            ]
        if join is True:
            q = q.join(Resource)
        q = q.filter(sql.or_(*filters_or))
        q = q.filter(sql.and_(*filters_and))
        if one is True:
            q = q.one_or_none()
        else:
            q = q.all()
        return q

    def get_track_by_uuid(self, session, uuid, join=False):
        q = session.query(Track)
        if join is True:
            q = q.join(Resource)
        q = q.filter(Track.uuid == uuid).one_or_none()
        return q

    def get_resource_by_uuid(self, session, uuid, join=False):
        q = session.query(Resource)
        if join is True:
            q = q.join(Track)
        q = q.filter(Resource.uuid == uuid).one_or_none()
        return q

    def get_resource_by_path(self, session, path, join=False):
        q = session.query(Resource)
        if join is True:
            q = q.join(Track)
        q = q.filter(Resource.path == path).one_or_none()
        return q

    def update_resource_by_path(self, session, path):
        res = self.get_resource_by_path(session, path)
        if res is None:
            res = Resource()
            res.track = Track()
        parse_resource(res, path)
        session.add(res)

    def clean_resources(self, session, paths):
        res = session.query(Resource)\
                .filter(~Resource.path.in_(paths))\
                .all()
        for r in res:
            session.delete(r)
