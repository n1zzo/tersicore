# MusicLibrary

## Configuration

There are two configuration files: config.ini specifies how this software should
behave and logging.conf specify how logging should work. In the docs/conf
directory you can find some examples. Further logging documentation can be found
[here][python-logging-config-dictschema].

You should initialize the Config object once. You can optionally specify a
config directory and override default file names.

    from tersicore.config import Config
    config = Config('/var/tersicore', 'tersicore.conf', 'log.conf')

Tersicore and logging configurations are shown to the user as dictionaries.

    conf_tersicore = config.tersicore
    conf_logging = config.logging
    
    conf_db = conf_tersicore['DATABASE']

## Database

### Workflow

If your module needs database access you have to initialize it once.
tersicore.

    from tersicore.database import Database
    db = Database(driver='sqlite', path='test.db')

Database operations must be grouped in transactions. If any operation fails the
whole transaction will be aborted and the database will remain unchanged. The
session is the context of the transaction and must be obtained from the Database
object.

    with db.get_session() as session:
        # database operations here

If you need to add a new Track or a Resource to the database you have to create
a new instance of the Track/Resource object, they can be found in `database.py`.
The session's add method will try to add the object to the database.
From now on the object and its entry in the database will be kept in sync as
long as the session will remain open.
The new Track or Resource will get a new uuid only once it gets its
way to the Database.

    from tersicore.database import Track, Resource
    
    with db.get_session() as session:
        track = Track(title='some data' ...)
        res = [Resource(path='some other data' ...),
               Resource(path='some other data' ...)]
        track.resources = res
        session.add(track)

If you need to remove the row linked to an existing object all you need is the
`session.delete()` method. If you delete a Track object you'll remove all of
its Resource objects automatically. If you delete every Resource object for a
Track you'll remove the latter automatically too.

    with db.get_session() as session:
        session.delete(track)
        # ...OR...
        session.delete(track.resources[0], track.resources[1])

If you need to search a row using an indexed column (uuid for Track, uuid and
path for Resource) you should use `get_track_by_uuid()`,
`get_resource_by_uuid()`, `get_resource_by_path()`. If you pass the `join=True`
argument, found Track objects will have their `resources` attributed populated
and Resource objects their `track` attribute.

    with db.get_session() as session:
        res = db.get_track_by_path(session, '/tmp/test.ogg', join=True)
        track = res.track
        session.delete(track)

If you need a fulltext search with filters you should use `get_tracks()`
instead. If you are looking for a single object pass `one=True`: the function
will either return a single Track object or None if the query returns zero or
more than one elements.

    with db.get_session() as session:
        tracks = db.get_tracks(session,
            text='the cooler', artist='black sun empire')

### Tables

#### resources

| Field           | Type            | Null | Key | Default | Extra          |
| :---------------| :-------------- | :--- | :-- | :------ | :------------- |
| uuid            | VARCHAR[32]     | NO   | PRI | NULL    | auto_increment |
| track_uuid      | VARCHAR[32]     | NO   |     | NULL    |                |
| last_modified   | TIMESTAMP       | NO   |     | NULL    |                |
| codec           | INTEGER         | NO   |     | NULL    |                |
| bitrate         | INTEGER         | NO   |     | NULL    |                |
| sample_rate     | INTEGER         | NO   |     | NULL    |                |
| path            | VARCHAR[1024]   | NO   |     | NULL    |                |

#### tracks

| Field           | Type            | Null | Key | Default | Extra          |
| :---------------| :---------------| :--- | :-- | :------ | :------------- |
| uuid            | VARCHAR[32]     | NO   | PRI | NULL    | auto_increment |
| track_number    | INTEGER         |      |     | NULL    |                |
| total_tracks    | INTEGER         |      |     | NULL    |                |
| disc_number     | INTEGER         |      |     | NULL    |                |
| total_discs     | INTEGER         |      |     | NULL    |                |
| title           | VARCHAR[256]    |      |     | NULL    |                |
| artist          | VARCHAR[256]    |      |     | NULL    |                |
| album_artist    | VARCHAR[256]    |      |     | NULL    |                |
| date            | VARCHAR[256]    |      |     | NULL    |                |
| label           | VARCHAR[256]    |      |     | NULL    |                |
| ISRC            | VARCHAR[256]    |      |     | NULL    |                |


[python-logging-config-dictschema]: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
