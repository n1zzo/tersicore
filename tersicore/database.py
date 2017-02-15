import os
from contextlib import contextmanager
from uuid import uuid4

import sqlalchemy as sa
import sqlalchemy.ext.declarative
import sqlalchemy.ext.baked
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import relationship, backref, subqueryload

from tersicore.log import get_logger


# The database URL must follow RFC 1738 in the form
# dialect+driver://username:password@host:port/database
ENGINE_GENERIC = '{engine}://{user}:{password}@{host}:{port}/{database}'\
                 '?charset=utf8'
ENGINE_SQLITE = 'sqlite:///{path}?charset=utf8'
ENGINE_SQLITE_MEMORY = 'sqlite://?charset=utf8'

# TODO: implement date!
COLUMN_TYPES = (int, str, bool)


def new_uuid():
    return uuid4().hex


Base = sqlalchemy.ext.declarative.declarative_base()
bakery = sqlalchemy.ext.baked.bakery()
log = get_logger('database')


class Database:
    """
    Handle database operations."
    """

    Session = None
    engine = None

    def __init__(self, **kwargs):
        """
        Initialize database connection.

        :param engine: The SQLAlchemy database backend in the form
                       dialect+driver where dialect is the name of a SQLAlchemy
                       dialect (sqlite, mysql, postgresql, oracle or mssql) and
                       driver is the name of the DBAPI in all lowercase
                       letters. If driver is not specified the default DBAPI
                       will be imported if available.
        :param path: Only for SQLite. Path to database. If not specified the
                     database will be kept in memory (should be used only for
                     testing).
        :param host:
        :param port:
        :param database:
        :param user:
        :param password:
        """

        if kwargs['engine'] == 'sqlite':
            if 'path' in kwargs:
                url = ENGINE_SQLITE.format(path=os.sep+kwargs['path'])
            else:
                url = ENGINE_SQLITE_MEMORY
        else:
            url = ENGINE_GENERIC.format(**kwargs)

        self.engine = sa.create_engine(url)
        self.Session = sa.orm.sessionmaker(bind=self.engine)

        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
        except Exception as e:
            log.error('Error performing transaction: %s', e)
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()


class Entry:
    def __repr__(self):
        return "<{}({})>"\
            .format(self.__class__.__name__, ", ".join([
                "{}='{}'".format(k, v)
                for k, v in self.items()
                ]))

    def keys(self):
        return [k
                for k, v in self.__dict__.items()
                if isinstance(v, COLUMN_TYPES)
                ]

    def items(self):
        return {k: v
                for k, v in self.__dict__.items()
                if isinstance(v, COLUMN_TYPES)
                }

    def items_ext(self):
        # Step #1
        d = self.items()
        # Step #2
        # Since, for example, Track has no explicit resources attribute because
        # it is backreferenced from Resource we need a little workaround to
        # make sure all relationships are caught.
        # __mapper__.relationships is a list of tuple where the first element
        # of the tuple is the name of the relationship.
        relationships = self.__mapper__.relationships.keys()
        for r in relationships:
            rel = getattr(self, r)
            # If the relationship points to multiple rows we run .items() again
            # for each element and add this new list to the dictionary
            if isinstance(rel, list):
                d[r] = [e.items() for e in rel]
        return d


class Track(Entry, Base):
    __tablename__ = 'tracks'

    uuid = Column(String(32), primary_key=True, default=new_uuid)
    track_number = Column(Integer)
    total_tracks = Column(Integer)
    disc_number = Column(Integer)
    total_discs = Column(Integer)
    title = Column(String(256))
    artist = Column(String(256))
    album_artist = Column(String(256))
    album = Column(String(256))
    compilation = Column(Boolean)
    date = Column(Date)
    label = Column(String(256))
    isrc = Column(String(256))


class Resource(Entry, Base):
    __tablename__ = 'resources'

    uuid = Column(String(32), primary_key=True, default=new_uuid)
    track_uuid = Column(String(32), ForeignKey('tracks.uuid'),
                        nullable=False)
    path = Column(String(1024), nullable=False, unique=True)
    codec = Column(String(16), nullable=False)
    sample_rate = Column(Integer, nullable=False)
    bitrate = Column(Integer, nullable=False)

    track = relationship(Track,
                         backref=backref('resources',
                                         single_parent=True,
                                         uselist=True
                                         )
                         )


def search_tracks(session, **kwargs):
    q = bakery(lambda s: s.query(Track)
                          .join(Track.resources)
                          .options(subqueryload(Track.resources)))
    for k, v in kwargs.items():
        if k in Track.keys():
            q += lambda f: f.filter(getattr(Track, k)
                                    .like('%{}%'.format(sa.bindparam(k))))
    result = q(session).params(**kwargs).all()
    return result
