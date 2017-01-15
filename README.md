# MusicLibrary

scanner --> database
user --> client --> database
client -[rpc]-> scanner  (???)
client -[rpc]-> transcoder
transcoder -> database -> user  (caching?)

## DB Scheme

TODO: since it will be federated use UUIDs instead of numeric IDs.
      everything the user can stream is a media resource. The user
      initially upload an original resource, but in the database
      there will be multiple resource for a single track: the
      original one and transcoded copies. Update db schema accordingly.

Users
| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| ID                       | SQLUBIGINT           | NO   | PRI | NULL    | auto_increment |

Paths
| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| ID                       | SQLUBIGINT           | NO   | PRI | NULL    | auto_increment |
| Path                     | SQLCHAR *            | NO   |     | NULL    |                |
| Owner                    | SQLUBIGINT           | NO   |     | NULL    |                |

Tracks
| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
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

## Internal APIs

def methodName(params) -> returnValue
private function   _func(params)
public  function   func(params)

class DB:
    def connect()
    def init()
    def add_track(string reource_path, tag) -> ID
    def update_track(tag) -> ID
    def get_path(ID) -> path
    def get_tag(ID) -> tag
    def search_keyword(keyword) -> IDlist

class Scanner:
    def _get_paths_from_db()
    def _get_file_info(string path)
    def job_add(string path) -> int jobid
    def job_status(int jobid)
    def job_stop(int jobid)
    def job_stop_all()
    def job_remove(int jobid)
    def job_remove_all()

class REST:
    def search(keyword) -> {albums : [albums], artists : [artists], titles : [titles]}
    def list_artists() ->  [artists]
    def list_albums() -> [albums]
    def list_titles() -> [titles]
    def get_resources(ID)

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

    Scanner --> DB.add_track(tag)

    repeat until complete path traversal


2) Database update

User --> Launch Software
DB --> connect(), if database is empty init()
Software --> inotify changed file in config[BaseDirectory]
Software --> for every changed file

    Scanner --> open file and read tag

    Scanner --> DB.update_track(tag)

    repeat until all the new files have been read
