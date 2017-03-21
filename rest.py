from flask import Flask, jsonify, abort, make_response, send_file, request
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


@app.route("/")
def greet():
    return "MusicLibrary - Tersicore"


@app.route('/tracks', methods=['GET'])
def get_tracks():
    with db.get_session() as session:
        tracks = session.query(Track).all()
        tracks = [dict(t) for t in tracks]
    return jsonify(tracks)


@app.route('/stream', methods=['GET'])
def get_resource():
    res_uuid = request.args.get("uuid")
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
