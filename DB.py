from config import get_config
from contextlib import contextmanager
import pyodbc
import uuid

class Database:
    ODBC_CONNECT_STRING = (
            "DRIVER={};SERVER={};PORT={};DATABASE={};UID={};PWD={}")

    QUERY_CREATE_TABLE_USERS = (
            "CREATE TABLE  Users ("
            "    ID        BIGINT        NOT NULL  AUTO_INCREMENT,"
            "    username  VARCHAR(256)  NOT NULL,"
            "    pw_hash   BINARY(64)    NOT NULL,"
            "    pw_salt   BINARY(64)    NOT NULL,"
            "    PRIMARY KEY(ID));")

    QUERY_CREATE_TABLE_TRACKS = (
            "CREATE TABLE Tracks ("
            "    UUID          BINARY(16)    NOT NULL,"
            "    track_number  INTEGER,"
            "    total_tracks  INTEGER,"
            "    disc_number   INTEGER,"
            "    total_discs   INTEGER,"
            "    title         VARCHAR(256)  NOT NULL,"
            "    artist        VARCHAR(256)  NOT NULL,"
            "    album_artist  VARCHAR(256),"
            "    date          VARCHAR(256),"
            "    label         VARCHAR(256),"
            "    ISRC          VARCHAR(256),"
            "    PRIMARY KEY(UUID));")

    QUERY_CREATE_TABLE_LIBRARIES = (
            "CREATE TABLE Libraries ("
            "    UUID      BINARY(16)    NOT NULL,"
            "    base_dir  VARCHAR(256)  NOT NULL,"
            "    owner     BIGINT        NOT NULL,"
            "    PRIMARY KEY(UUID),"
            "    FOREIGN KEY(owner) REFERENCES Users(ID));")

    QUERY_CREATE_TABLE_RESOURCES = (
            "CREATE TABLE Resources ("
            "    UUID           BINARY(16)    NOT NULL,"
            "    track_UUID     BINARY(16)    NOT NULL,"
            "    last_modified  TIMESTAMP     NOT NULL,"
            "    codec          SMALLINT      NOT NULL,"
            "    bitrate        SMALLINT      NOT NULL,"
            "    owner          BIGINT        NOT NULL,"
            "    path           VARCHAR(256)  NOT NULL,"
            "    PRIMARY KEY(UUID),"
            "    FOREIGN KEY(track_UUID) REFERENCES Tracks(UUID));")

    QUERY_DROP_ALL_TABLES = (
            "DROP TABLE IF EXISTS Resources, Libraries, Tracks, Users;")

    QUERY_INSERT_TRACK = (
            "INSERT INTO Tracks("
            "    UUID, track_number, total_tracks, disc_number, total_discs,"
            "    title, artist, album_artist, date, label, ISRC)"
            "VALUES (UNHEX(?),?,?,?,?,?,?,?,?,?,?);")

    QUERY_UPDATE_TRACK = (
            "UPDATE Tracks"
            "    SET track_number=?, total_tracks=?, disc_number=?,"
            "        total_discs=?, title=?, artist=?, album_artist=?,"
            "        date=?,label=?,ISRC=?"
            "    WHERE UUID = UNHEX(?);")

    connection = None

    def __init__(self):
        # Parse configuration file and generate connection string
        config = get_config()

        self._connect(
                driver   = config['DATABASE']['Driver'],
                host     = config['DATABASE']['Host'],
                port     = config['DATABASE']['Port'],
                database = config['DATABASE']['Database'],
                user     = config['DATABASE']['User'],
                password = config['DATABASE']['Password'])

        with self._get_cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            if cursor.tables().fetchone() is None:
                self._create_tables()

    def _connect(self, driver=None, host=None, port=None, database=None,
            user=None, password=None):
        self.connection = pyodbc.connect(self.ODBC_CONNECT_STRING.format(
                driver, host, port, database, user, password))

        self.connection.autocommit = False
        self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.connection.setencoding(encoding='utf-8')

    def _disconnect(self):
        self.connection.close()

    @contextmanager
    def _get_cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
        except pyodbc.DatabaseError as err:
            cursor.rollback()
        else:
            cursor.commit()
        finally:
            cursor.close()

    def _create_tables(self):
        with self._get_cursor() as cursor:
            cursor.execute(self.QUERY_CREATE_TABLE_USERS)
            cursor.execute(self.QUERY_CREATE_TABLE_TRACKS)
            cursor.execute(self.QUERY_CREATE_TABLE_LIBRARIES)
            cursor.execute(self.QUERY_CREATE_TABLE_RESOURCES)

    def _drop_tables(self):
        with self._get_cursor() as cursor:
            cursor.execute(self.QUERY_DROP_ALL_TABLES)

    def add_track(self, tag):
        UUID = uuid.uuid4()
        with self._get_cursor() as cursor:
            cursor.execute(self.QUERY_INSERT_TRACK,
                    UUID.hex, tag["track_number"], tag["total_tracks"],
                    tag["disc_number"], tag["total_discs"],
                    tag["title"], tag["artist"], tag["album_artist"],
                    tag["date"], tag["label"], tag["isrc"])
        return UUID

    def update_track(self, UUID, tag):
        with self._get_cursor() as cursor:
            cursor.execute(self.QUERY_UPDATE_TRACK,
                    tag["track_number"], tag["total_tracks"],
                    tag["disc_number"], tag["total_discs"],
                    tag["title"], tag["artist"], tag["album_artist"],
                    tag["date"], tag["label"], tag["isrc"], UUID.hex)

if __name__ == "__main__":
    db = Database()

    test_tag =  {
            "track_number": 3,
            "total_tracks": 20,
            "disc_number": 2,
            "total_discs": 1,
            "title": "Funny Title",
            "artist": "Happy Artists",
            "album_artist": "Happy Artists Collection",
            "date": "20-12-2016",
            "label": "Greedy Records",
            "isrc": "ASCGM2345" }

    id = db.add_track(test_tag)
    print("Inserted new track with UUID", str(id))

    test_tag["title"] = "NEWTITLE"
    db.update_track(id, test_tag)

    db._drop_tables()
