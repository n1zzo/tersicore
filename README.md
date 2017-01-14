# MusicLibrary

scanner --> database
user --> web interface --> database
web interface -[rpc]-> scanner
web interface -[rpc]-> transcoder
transcoder -> database -> user

## DB Scheme


Users
+--------------------------+----------------------+------+-----+---------+----------------+
| Field                    | Type                 | Null | Key | Default | Extra          |
+--------------------------+----------------------+------+-----+---------+----------------+
| ID                       | SQLUBIGINT           | NO   | PRI | NULL    | auto_increment |
+--------------------------+----------------------+------+-----+---------+----------------+

Paths
+--------------------------+----------------------+------+-----+---------+----------------+
| Field                    | Type                 | Null | Key | Default | Extra          |
+--------------------------+----------------------+------+-----+---------+----------------+
| ID                       | SQLUBIGINT           | NO   | PRI | NULL    | auto_increment |
| Path                     | SQLCHAR *            | NO   |     | NULL    |                |
| Owner                    | SQLUBIGINT           | NO   |     | NULL    |                |
+--------------------------+----------------------+------+-----+---------+----------------+

Tracks
+--------------------------+----------------------+------+-----+---------+----------------+
| Field                    | Type                 | Null | Key | Default | Extra          |
+--------------------------+----------------------+------+-----+---------+----------------+
| ID                       | SQLUBIGINT           | NO   | PRI | NULL    | auto_increment |
| Track_number             | SQLUINTEGER          |      |     | NULL    |                |
| Total_tracks             | SQLUINTEGER          |      |     | NULL    |                |
| Disc_number              | SQLUINTEGER          |      |     | NULL    |                |
| Total_discs              | SQLUINTEGER          |      |     | NULL    |                |
| Title                    | SQLCHAR *            | NO   |     | NULL    |                |
| Artist                   | SQLCHAR *            | NO   |     | NULL    |                |
| AlbumArtist              | SQLCHAR *            |      |     | NULL    |                |
| Codec                    | SQLUSMALLINT         | NO   |     | NULL    |                |
| Bitrate                  | SQLUSMALLINT         | NO   |     | NULL    |                |
| Date                     | SQLCHAR *            |      |     | NULL    |                |
| Label / Organization     | SQLCHAR *            |      |     | NULL    |                |
| ISRC                     | SQLCHAR *            |      |     | NULL    |                |
| LastModified             | SQL_TIMESTAMP_STRUCT | NO   |     | NULL    |                |
+--------------------------+----------------------+------+-----+---------+----------------+

## Internal APIs

def methodName(params) -> returnValue

class DB:
    def connect()
    def init()
    def addTrack(tag) -> ID
    def updateTrack(tag) -> ID
    def getPath(ID) -> path
    def getTag(ID) -> tag
    def searchKeyword(keyword) -> IDlist

class Scanner:
    def start()
    def pause()
    def stop()

class REST:
    def search(keyword) -> {albums : [albums], artists : [artists], titles : [titles]}
    def listArtists() ->  [artists]
    def listAlbums() -> [albums]
    def listTitles() -> [titles]
    def enqueue(ID) -> [queueTitles]
    def clearQueue()
    def play(ID)
    def stop()
    def pause()
    def next()
    def prev()

class Core:
    def stream(path) -> streamID
    def stop(streamID)

## Configuration file

[LIBRARY]
BaseDirectory = /home/user/Music

[DATABASE]
Driver = {SQL Server}
Server = localhost
Database = test
Username = me
Password = me2

##  Tag parsing

https://mutagen.readthedocs.io/en/latest/

## Database interface

https://wiki.python.org/moin/DatabaseInterfaces
ODBC support:
https://github.com/mkleehammer/pyodbc
Data types
https://msdn.microsoft.com/en-us/library/ms714556(v=vs.85).aspx

## Web Interface

http://cherrypy.org/

## Architecture

The software will have a modular structure, every piece will communicate with each other via IPC.
The main components will be:
    - Library Scanner Daemon
    - Media Backend (read + [transcode +] stream) accessible via REST
    - Web Interface
    - DBMS

## Use case

1) Library bootstrap

User --> Launch Software
DB --> connect(), if database is empty init()
Software --> empty library
Software --> Scanner.start()

    Scanner --> scan config[BaseDirectory] path and for every file

    Scanner --> open file and read tag

    Scanner --> DB.addTrack(tag)

    repeat until complete path traversal


2) Database update

User --> Launch Software
DB --> connect(), if database is empty init()
Software --> inotify changed file in config[BaseDirectory]
Software --> for every changed file

    Scanner --> open file and read tag

    Scanner --> DB.updateTrack(tag)

    repeat until all the new files have been read
