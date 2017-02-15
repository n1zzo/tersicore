from flask import Flask, jsonify, abort, make_response, send_file
from io import BytesIO

from tersicore.config import Config
from tersicore.log import init_logging, get_logger
from tersicore.database import Database, Resource, search_tracks

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
        tracks = [t.items_ext() for t in search_tracks(session)]
    return jsonify(tracks)


@app.route('/resources/<string:res_uuid>', methods=['GET'])
def get_resource(res_uuid):
    with db.get_session() as session:
        res = session.query(Resource).get(res_uuid)
        if res is None:
            abort(404)
        try:
            with open(res.path, 'rb') as fh:
                mimetype = 'audio/{}'.format(res.codec)
                return send_file(BytesIO(fh.read()),
                                 mimetype=mimetype)
        except FileNotFoundError:
            abort(500)


@app.errorhandler(404)
def http_404(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.errorhandler(500)
def http_500(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
