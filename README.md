# MusicLibrary

scanner --> database
user --> client --> database
client -[rpc]-> scanner  (???)
client -[rpc]-> transcoder
transcoder -> database -> user  (caching?)git

## TODOs

- since it will be federated use UUIDs instead of numeric IDs.
      everything the user can stream is a media resource. The user
      initially upload an original resource, but in the database
      there will be multiple resource for a single track: the
      original one and transcoded copies. Update db schema accordingly.

- Define how to do multithreading and IPC in python


## DB Scheme

Users

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| ID                       | BIGINT               | NO   | PRI | NULL    | auto_increment |

Libraries

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| UUID                     | BINARY[16]           | NO   | PRI | NULL    | auto_increment |
| base_dir                 | VARCHAR[256]         | NO   |     | NULL    |                |
| owner                    | BIGINT               | NO   |     | NULL    |                |

Resources

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| UUID                     | BINARY[16]           | NO   | PRI | NULL    | auto_increment |
| track_UUID               | VARCHAR[16]          | NO   |     | NULL    |                |
| last_modified            | TIMESTAMP            | NO   |     | NULL    |                |
| codec                    | SMALLINT             | NO   |     | NULL    |                |
| bitrate                  | SMALLINT             | NO   |     | NULL    |                |
| owner                    | BIGINT               | NO   |     | NULL    |                |
| path                     | VARCHAR[256]         | NO   |     | NULL    |                |

Tracks

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| UUID                     | BINARY[16]           | NO   | PRI | NULL    | auto_increment |
| track_number             | INTEGER              |      |     | NULL    |                |
| total_tracks             | INTEGER              |      |     | NULL    |                |
| disc_number              | INTEGER              |      |     | NULL    |                |
| total_discs              | INTEGER              |      |     | NULL    |                |
| title                    | VARCHAR[256]         | NO   |     | NULL    |                |
| artist                   | VARCHAR[256]         | NO   |     | NULL    |                |
| album_artist             | VARCHAR[256]         |      |     | NULL    |                |
| date                     | VARCHAR[256]         |      |     | NULL    |                |
| label                    | VARCHAR[256]         |      |     | NULL    |                |
| ISRC                     | VARCHAR[256]         |      |     | NULL    |                |


## Internal APIs

```
def methodName(params) -> returnValue
private function   _func(params)
public  function   func(params)
```

```
class DB:
    def _init()
    def add_track(path, tag) -> ID
    def update_track(ID, tag)
    def get_path(ID) -> path
    def get_tag(ID) -> tag
    def search_keyword(keyword) -> IDlist
```

```
class Scanner:
    def _get_paths_from_db()
    def _get_file_info(string path)
    def job_add(string path) -> int jobid
    def job_status(int jobid)
    def job_stop(int jobid)
    def job_stop_all()
    def job_remove(int jobid)
    def job_remove_all()
```

```
class REST:
    def search(keyword) -> {albums : [albums], artists : [artists], titles : [titles]}
    def list_artists() ->  [artists]
    def list_albums() -> [albums]
    def list_titles() -> [titles]
    def get_resources(ID)
```

```
class Core:
    def stream(path) -> streamID
    def stop(streamID)
```

## Configuration file

```
[DATABASE]
Driver = {SQL Server}
Server = localhost
Port = 3210
Database = test
Username = me
Password = me2
```

##  Tag parsing

https://mutagen.readthedocs.io/en/latest/

## Database interface

https://wiki.python.org/moin/DatabaseInterfaces \
ODBC support:
https://github.com/mkleehammer/pyodbc \
Data types
https://msdn.microsoft.com/en-us/library/ms714556(v=vs.85).aspx
We are storing UUID according to RFC4122

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

User --> Launch Software \
DB --> connect(), if database is empty init() \
Software --> empty library \
Software --> Scanner.start()

    Scanner --> scan config[BaseDirectory] path and for every file

    Scanner --> open file and read tag

    Scanner --> DB.add_track(tag)

    repeat until complete path traversal


2) Database update

User --> Launch Software \
DB --> connect(), if database is empty init() \
Software --> inotify changed file in config[BaseDirectory] \
Software --> for every changed file

    Scanner --> open file and read tag

    Scanner --> DB.update_track(tag)

    repeat until all the new files have been read

## Installation

Instructions to install on x86_64 linux:

- install MySQL server
- pip install -r requirements.txt
- download [MySQL ODBC connector](http://dev.mysql.com/get/Downloads/Connector-ODBC/5.3/mysql-connector-odbc-5.3.7-linux-glibc2.5-x86-64bit.tar.gz)
- extract it and move libmyodbc5a.so to /usr/lib/x86_64-linux-gnu/odbc/
- create the file /etc/odbcinst.ini with the following content
```
[MySQL]
Description = ODBC for MySQL
Driver = /usr/lib/x86_64-linux-gnu/odbc/libmyodbc5a.so
Setup = /usr/lib/x86_64-linux-gnu/odbc/libodbcmyS.so
FileUsage = 1
```
- edit config.ini to reflect your database settings
- done!
