# MusicLibrary

## DB schema

### resources

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| uuid                     | VARCHAR[32]          | NO   | PRI | NULL    | auto_increment |
| track_uuid               | VARCHAR[32]          | NO   |     | NULL    |                |
| last_modified            | TIMESTAMP            | NO   |     | NULL    |                |
| codec                    | INTEGER              | NO   |     | NULL    |                |
| bitrate                  | INTEGER              | NO   |     | NULL    |                |
| sample_rate              | INTEGER              | NO   |     | NULL    |                |
| path                     | VARCHAR[1024]        | NO   |     | NULL    |                |

### tracks

| Field                    | Type                 | Null | Key | Default | Extra          |
| :----------------------- | :------------------- | :--- | :-- | :------ | :------------- |
| uuid                     | VARCHAR[32]          | NO   | PRI | NULL    | auto_increment |
| track_number             | INTEGER              |      |     | NULL    |                |
| total_tracks             | INTEGER              |      |     | NULL    |                |
| disc_number              | INTEGER              |      |     | NULL    |                |
| total_discs              | INTEGER              |      |     | NULL    |                |
| title                    | VARCHAR[256]         |      |     | NULL    |                |
| artist                   | VARCHAR[256]         |      |     | NULL    |                |
| album_artist             | VARCHAR[256]         |      |     | NULL    |                |
| date                     | VARCHAR[256]         |      |     | NULL    |                |
| label                    | VARCHAR[256]         |      |     | NULL    |                |
| ISRC                     | VARCHAR[256]         |      |     | NULL    |                |
