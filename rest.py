from flask import Flask, jsonify, abort, make_response, send_file
from io import BytesIO

from tersicore.config import Config
from tersicore.log import init_logging, get_logger
from tersicore.database import Database

config = Config()

config_logging = config.logging
init_logging(config_logging)
log = get_logger('rest')

config_database = config.tersicore['DATABASE']
db = Database(**config_database)

app = Flask(__name__)


@app.route("/")
def greet():
    return "MusicLibrary - Tersicore"


@app.route('/tracks', methods=['GET'])
def get_tracks():
    tracks = []
    with db.get_session() as session:
        tracks = db.get_tracks(session, join=True)
        tracks = [t.dict() for t in tracks]
    return jsonify(tracks)


@app.route('/resources/<string:res_uuid>', methods=['GET'])
def get_resource(res_uuid):
    with db.get_session() as session:
        res = db.get_resource_by_uuid(session, res_uuid)
    if res is None:
        abort(404)
    path = res.path
    with open(path, 'rb') as res_file:
        mimetype = 'audio/{}'.format(res.codec)
        return send_file(BytesIO(res_file.read()),
                     mimetype=mimetype)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
