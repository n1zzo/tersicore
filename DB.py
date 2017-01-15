from config import get_config
import pyodbc
import uuid

# class DB:
#     def _init()
#     def connect()
#     def create_tables()
#     def add_track(path, tag) -> ID
#     def update_track(ID, tag)
#     def get_path(ID) -> path
#     def get_tag(ID) -> tag
#     def search_keyword(keyword) -> IDlist

CREATE_TRACKS = ("CREATE TABLE Tracks ("
                 "UUID BINARY(16) PRIMARY KEY, track_number INTEGER, "
                 "total_tracks INTEGER, disc_number INTEGER, "
                 "total_discs INTEGER, title VARCHAR(256) NOT NULL, "
                 "artist VARCHAR(256) NOT NULL, album_artist VARCHAR(256), "
                 "date VARCHAR(256), label VARCHAR(256), ISRC VARCHAR(256))")

INSERT_TRACK = ("INSERT INTO Tracks(UUID, track_number, total_tracks, "
                "disc_number, total_discs, title, artist, album_artist, "
                "date, label, ISRC) values (UNHEX(?),?,?,?,?,?,?,?,?,?,?)")

UPDATE_TRACK = ("UPDATE Tracks SET track_number=?,total_tracks=?,"
                "disc_number=?,total_discs=?,title=?,artist=?,album_artist=?,"
                "date=?,label=?,ISRC=? WHERE UUID = UNHEX(?);")


class DB:
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
        self.cursor.execute(CREATE_TRACKS)
        self.cursor.commit()

    def add_track(self, tag):
        UUID = uuid.uuid4()
        self.cursor.execute(INSERT_TRACK, UUID.hex, tag["track_number"],
                            tag["total_tracks"], tag["disc_number"],
                            tag["total_discs"], tag["title"], tag["artist"],
                            tag["album_artist"], tag["date"],
                            tag["label"], tag["isrc"])
        self.cursor.commit()
        return UUID

    def update_track(self, UUID, tag):
        self.cursor.execute(UPDATE_TRACK, tag["track_number"],
                            tag["total_tracks"], tag["disc_number"],
                            tag["total_discs"], tag["title"], tag["artist"],
                            tag["album_artist"], tag["date"],
                            tag["label"], tag["isrc"], UUID.hex)
        self.cursor.commit()

if __name__ == "__main__":
    db = DB()
    db.connect()
    # db.create_tables()

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
