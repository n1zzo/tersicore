from database import Database

import json
import falcon


class TracksRequest(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp):
        reply = []
        with self.db.get_session() as session:
            tracks = self.db.get_tracks(session, None)
            for track in tracks:
                reply.append({
                    'uuid': track.uuid,
                    'track_number': track.track_number,
                    'total_tracks': track.total_tracks,
                    'disc_number': track.disc_number,
                    'total_discs': track.total_discs,
                    'title': track.title,
                    'artist': track.artist,
                    'album': track.album,
                    'album_artist': track.album_artist,
                    'compilation': track.compilation,
                    'date': str(track.date),
                    'label': track.label,
                    'isrc': track.isrc,
                    'resources': [{
                        'path': resource.path,
                        'codec': resource.codec,
                        'bitrate': resource.bitrate
                        } for resource in track.resources]
                    })

        resp.body = json.dumps(reply, indent=4, sort_keys=True)


db = Database()

tracks_request = TracksRequest(db)

app = falcon.API()
app.add_route('/tracks', tracks_request)
