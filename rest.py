from flask import Flask, jsonify, abort, make_response, send_file
from flask_hmac import Hmac
from io import BytesIO

from tersicore.config import Config
from tersicore.log import init_logging, get_logger
from tersicore.database import Database, Track, Resource

config = Config()

config_logging = config.logging
init_logging(config_logging)
log = get_logger('rest')

config_database = config.tersicore['DATABASE']
db = Database(**config_database)

app = Flask(__name__)
app.config.from_object('rest_config.Config')
hm = Hmac(app)


@app.route("/")
def greet():
    return "MusicLibrary - Tersicore"


@app.route('/tracks', methods=['GET'])
@hm.check_hmac
def get_tracks():
    with db.get_session() as session:
        tracks = session.query(Track).all()
        tracks = [dict(t) for t in tracks]
    return jsonify(tracks)


@app.route('/tracks/<string:track_uuid>', methods=['GET'])
@hm.check_hmac
def get_track(track_uuid):
    with db.get_session() as session:
        track = session.query(Track)\
                .filter(Track.uuid == track_uuid)\
                .one_or_none()
        track = dict(track)
    return jsonify(track)


@app.route('/stream/<string:res_uuid>', methods=['GET'])
@hm.check_hmac
def get_resource(res_uuid):
    try:
        with db.get_session() as session:
            res = session.query(Resource)\
                         .filter(Resource.uuid == res_uuid)\
                         .one_or_none()
        if res is None:
            abort(404)
        path = res.path
        with open(path, 'rb') as res_file:
            mimetype = 'audio/{}'.format(res.codec)
            return send_file(BytesIO(res_file.read()),
                             mimetype=mimetype)
    except FileNotFoundError:
        abort(500)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
