import configparser
import pyodbc
import uuid

#class DB:
#    def _init()
#    def connect()
#    def create_tables()
#    def add_track(path, tag) -> ID
#    def update_track(ID, tag)
#    def get_path(ID) -> path
#    def get_tag(ID) -> tag
#    def search_keyword(keyword) -> IDlist

CREATE_TRACKS = ("CREATE TABLE Tracks ("
                 "UUID BINARY(16) PRIMARY KEY, Track_number INTEGER, "
                 "Total_tracks INTEGER, Disc_number INTEGER, "
                 "Total_discs INTEGER, Title VARCHAR(256) NOT NULL, "
                 "Artist VARCHAR(256) NOT NULL, AlbumArtist VARCHAR(256), "
                 "Date VARCHAR(256), Label VARCHAR(256), ISRC VARCHAR(256))")

INSERT_TRACK = ("INSERT INTO PRODUCTS(UUID, Track_number, Total_tracks, "
                "Disc_number, Total_discs, Title, Artists, AlbumArtist, "
                "Date, Label, ISRC) values (UNHEX(?),?,?,?,?,?,?,?,?,?,?)")

class DB:
    conn_string = None
    cnxn = None
    cursor = None

    def __init__(self):
        # Parse configuration file and generate connection string
        config = configparser.ConfigParser()
        config.read('config.ini')

        driver = config['DATABASE']['Driver']
        server = config['DATABASE']['Server']
        port = config['DATABASE']['Port']
        database = config['DATABASE']['Database']
        socket = config['DATABASE']['Socket']
        uid = config['DATABASE']['UID']
        password = config['DATABASE']['Password']

        self.conn_string = ('DRIVER='+driver+';SERVER='+server+
                            ';PORT='+port+';DATABASE='+database+
                            ';SOCKET='+socket+';UID='+uid+';PWD='+password)

    def connect(self):
        self.cnxn = pyodbc.connect(self.conn_string)
        self.cursor = self.cnxn.cursor()

        self.cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.cnxn.setencoding(encoding='utf-8')

    def create_tables(self):
        self.cursor.execute(CREATE_TRACKS)
        self.cursor.commit()

    def add_track(ID, tag):
        UUID = uuid.uuid4()
        self.cursor.execute(INSERT_TRACK, UUID.hex, tag.track_number,
                            tag.total_discs, tag.title, tag.artists,
                            tag.album, tag.albumArtist, tag.date, tag.label,
                            tag.isrc)

if __name__ == "__main__":
    db = DB()
    db.connect()
    #db.create_tables()

