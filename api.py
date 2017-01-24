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
                track_dict = track.dict()
                track_dict.update({
                    'resources': res.dict()
                    for res in track.resources
                    })
                reply.append(track_dict)
        resp.body = json.dumps(reply, indent=4, sort_keys=True)


db = Database()

tracks_request = TracksRequest(db)

app = falcon.API()
app.add_route('/tracks', tracks_request)
