from flask import Flask, jsonify

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
    with db.get_session() as session:
        tracks = db.get_tracks(session, join=True)
        tracks_dict = [t.to_dict() for t in tracks]
        return jsonify(tracks_dict)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
