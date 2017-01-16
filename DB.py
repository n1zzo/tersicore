from config import get_config
import pyodbc
import uuid

# class DB:
#     def _init()
#     def connect()
#     def create_tables()
#     def drop_tables()
#     def add_track(path, info, tag) -> ID
#     def update_track(ID, tag)
#     def get_path(ID) -> path
#     def get_tag(ID) -> tag
#     def search_keyword(keyword) -> IDlist


class DB:
    QUERY_CREATE_TABLE_USERS = (
            "CREATE TABLE  Users ("
                "ID        BIGINT        NOT NULL  AUTO_INCREMENT,"
                "username  VARCHAR(256)  NOT NULL,"
                "pw_hash   BINARY(64)    NOT NULL,"
                "pw_salt   BINARY(64)    NOT NULL,"
                "PRIMARY KEY(ID));")

    QUERY_CREATE_TABLE_TRACKS = (
            "CREATE TABLE Tracks ("
                "UUID          BINARY(16)    NOT NULL,"
                "track_number  INTEGER,"
                "total_tracks  INTEGER,"
                "disc_number   INTEGER,"
                "total_discs   INTEGER,"
                "title         VARCHAR(256)  NOT NULL,"
                "artist        VARCHAR(256)  NOT NULL,"
                "album_artist  VARCHAR(256),"
                "date          VARCHAR(256),"
                "label         VARCHAR(256),"
                "ISRC          VARCHAR(256),"
                "PRIMARY KEY(UUID));")

    QUERY_CREATE_TABLE_LIBRARIES = (
            "CREATE TABLE Libraries ("
                "UUID      BINARY(16)    NOT NULL,"
                "base_dir  VARCHAR(256)  NOT NULL,"
                "owner     BIGINT        NOT NULL,"
                "PRIMARY KEY(UUID),"
                "FOREIGN KEY(owner) REFERENCES Users(ID));")

    QUERY_CREATE_TABLE_RESOURCES = (
            "CREATE TABLE Resources ("
                "UUID           BINARY(16)    NOT NULL,"
                "track_UUID     BINARY(16)    NOT NULL,"
                "last_modified  TIMESTAMP     NOT NULL,"
                "codec          SMALLINT      NOT NULL,"
                "bitrate        SMALLINT      NOT NULL,"
                "owner          BIGINT        NOT NULL,"
                "path           VARCHAR(256)  NOT NULL,"
                "PRIMARY KEY(UUID),"
                "FOREIGN KEY(track_UUID) REFERENCES Tracks(UUID));")

    QUERY_DROP_ALL_TABLES = (
            "DROP TABLE IF EXISTS Resources, Libraries, Tracks, Users;")

    QUERY_INSERT_TRACK = (
            "INSERT INTO Tracks("
                "UUID, track_number, total_tracks, disc_number, total_discs,"
                "title, artist, album_artist, date, label, ISRC)"
            "VALUES (UNHEX(?),?,?,?,?,?,?,?,?,?,?);")

    QUERY_UPDATE_TRACK = (
            "UPDATE Tracks"
            "SET track_number=?, total_tracks=?, disc_number=?,"
                "total_discs=?, title=?, artist=?, album_artist=?,"
                "date=?,label=?,ISRC=?"
            "WHERE UUID = UNHEX(?);")

    conn_string = None
    cnxn = None
    cursor = None

    def __init__(self):
        # Parse configuration file and generate connection string
        config = get_config()

        driver = config['DATABASE']['Driver']
        server = config['DATABASE']['Server']
        port = config['DATABASE']['Port']
        database = config['DATABASE']['Database']
        socket = config['DATABASE']['Socket']
        uid = config['DATABASE']['UID']
        password = config['DATABASE']['Password']

        self.conn_string = 'DRIVER={};SERVER={};\
                            PORT={};DATABASE={};\
                            SOCKET={};UID={};PWD={}'.format(driver, server,
                                                            port, database,
                                                            socket, uid,
                                                            password)

    def connect(self):
        self.cnxn = pyodbc.connect(self.conn_string)
        self.cursor = self.cnxn.cursor()

        self.cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.cnxn.setencoding(encoding='utf-8')

    def create_tables(self):
        self.cursor.execute(QUERY_CREATE_TABLE_USERS)
        self.cursor.execute(QUERY_CREATE_TABLE_TRACKS)
        self.cursor.execute(QUERY_CREATE_TABLE_LIBRARIES)
        self.cursor.execute(QUERY_CREATE_TABLE_RESOURCES)
        self.cursor.commit()

    def drop_tables(self):
        self.cursor.execute(QUERY_DROP_ALL_TABLES)
        self.cursor.commit()

    def add_track(self, tag):
        UUID = uuid.uuid4()
        self.cursor.execute(QUERY_INSERT_TRACK, UUID.hex, tag["track_number"],
                            tag["total_tracks"], tag["disc_number"],
                            tag["total_discs"], tag["title"], tag["artist"],
                            tag["album_artist"], tag["date"],
                            tag["label"], tag["isrc"])
        self.cursor.commit()
        return UUID

    def update_track(self, UUID, tag):
        self.cursor.execute(QUERY_UPDATE_TRACK, tag["track_number"],
                            tag["total_tracks"], tag["disc_number"],
                            tag["total_discs"], tag["title"], tag["artist"],
                            tag["album_artist"], tag["date"],
                            tag["label"], tag["isrc"], UUID.hex)
        self.cursor.commit()

if __name__ == "__main__":
    db = DB()
    db.connect()
    db.drop_tables()
    db.create_tables()

    test_tag = {"track_number": 3,
                "total_tracks": 20,
                "disc_number": 2,
                "total_discs": 1,
                "title": "Funny Title",
                "artist": "Happy Artists",
                "album_artist": "Happy Artists Collection",
                "date": "20-12-2016",
                "label": "Greedy Records",
                "isrc": "ASCGM2345"}

    id = db.add_track(test_tag)
    print("Inserted new track with UUID", str(id))
    test_tag["title"] = "NEWTITLE"
    db.update_track(id, test_tag)
