from datetime import date

from database import Database


def test_database():
    db = Database()

    track1 = db.Track(
        track_number=1,
        total_tracks=2,
        disc_number=1,
        total_discs=1,
        title='Mr Happy mispelled',
        artist='DJ Hazard; Distorted Minds',
        album_artist='DJ Hazard; Distorted Minds',
        album='Mr Happy / Super Drunk',
        compilation=False,
        date=date(2007, 10, 8),
        label='Playaz Recordings',
        isrc='PLAYAZ002'
        )

    track2 = db.Track(
        track_number=2,
        total_tracks=2,
        disc_number=1,
        total_discs=1,
        title='Super Drunk',
        artist='DJ Hazard; Distorted Minds',
        album_artist='DJ Hazard; Distorted Minds',
        album='Mr Happy / Super Drunk',
        compilation=False,
        date=date(2007, 10, 8),
        label='Playaz Recordings',
        isrc='PLAYAZ002'
        )

    with db.get_session() as session:
        session.add(track1)
        session.add(track2)
        print("We just added:")
        print()
        print(track1, track2)
        print()
        print()

    with db.get_session() as session:
        session.add(track1)
        track1.title = 'Mr Happy'
        print("We just updated:")
        print()
        print(track1)
        print()
        print()

    with db.get_session() as session:
        session.add(track1)
        session.add(track2)
        track1.resources = [
            db.Resource(codec='ogg', bitrate='320', path='/music/track1.ogg'),
            db.Resource(codec='mp3', bitrate='192', path='/music/track1.mp3')
            ]
        track2.resources = [
            db.Resource(codec='ogg', bitrate='320', path='/music/track2.ogg'),
            db.Resource(codec='mp3', bitrate='192', path='/music/track2.mp3')
            ]
        print("We just added the following resources:")
        print()
        print(track1.resources, track2.resources)
        print()
        print()

    with db.get_session() as session:
        print("Query:")
        print()
        q = session.query(db.Track, db.Resource).join(db.Resource).all()
        print(q)


if __name__ == "__main__":
    test_database()
