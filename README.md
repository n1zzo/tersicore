# MusicLibrary

## Database

### Workflow

If your module needs database access you have to initialize it once. It will
automatically load its configuration from the `config.ini` file.

    from database import Database
    db = Database()

Database operations must be grouped in transactions. If any operation fails the
whole transaction will be aborted and the database will remain unchanged. The
session is the context of the transaction and must be asked for to the Database
object.

    with db.get_session() as session:
        # database operations here

If you need to add a new Track or a Resource to the database you need to create
a new Track/Resource object that can be found in the `database.py`. The session
will try to add the object to the database and from now the object and its entry
in the database will be kept in sync as long as the session is open. The new
Track or Resouce will get a new uuid only once it gets its way to the Database.

    from database import Track, Resource
    
    with db.get_session() as session:
        track = Track(title='some data' ...)
        res = [Resource(path='some other data' ...),
               Resource(path='some other data' ...)]
        track.resources = res
        session.add(track)

If you need to remove the row linked to an existing object all you need is the
`session.delete()` method. If you delete a Track object you'll remove each of
its Resource objects automatically. If you delete each Resource object for a
Track you'll remove the latter automatically too.

    with db.get_session() as session:
        session.delete(track)
        # ...OR...
        session.delete(track.resources[0], track.resources[1])

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
