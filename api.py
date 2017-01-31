from flask import Flask, jsonify
from database import Database
app = Flask(__name__)

db = None


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
    db = Database()
    app.run(host='0.0.0.0', debug=True)
