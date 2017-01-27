from database import Database, Track, Resource

from datetime import date
from uuid import uuid4


def test_insert(db):
    print("Testing database.")
    track_ = None
    track = Track(
        track_number=1,
        total_tracks=2,
        disc_number=1,
        total_discs=1,
        title='Mr Happy',
        artist='DJ Hazard; Distorted Minds',
        album_artist='DJ Hazard; Distorted Minds',
        album='Mr Happy / Super Drunk',
        compilation=False,
        date=date(2007, 10, 8),
        label='Playaz Recordings',
        isrc='PLAYAZ002',
        resources=[
            Resource(
                codec='ogg',
                bitrate='320',
                sample_rate='44100',
                path=uuid4().hex),
            Resource(
                codec='mp3',
                bitrate='192',
                sample_rate='44100',
                path=uuid4().hex)
            ]
         )

    with db.get_session() as session:
        print("Adding:", track)
        session.add(track)

    with db.get_session() as session:
        print("Query for uuid:", track.uuid)
        track_ = db.get_track_by_uuid(session, track.uuid)
        track_resources = track.resources
        print("Result:", track_, track_resources)

    with db.get_session() as session:
        print("Removing.")
        session.delete(track_)

    with db.get_session() as session:
        print("Checking...")
        track_ = db.get_track_by_uuid(session, track.uuid)
        if track_ is None:
            print("Track removed")
        else:
            print("Track NOT removed")
        for res in track.resources:
            res_ = db.get_resource_by_uuid(session, res.uuid)
            if res_ is None:
                print("Resource removed")

    track_ = None
    track = Track(
        track_number=1,
        total_tracks=2,
        disc_number=1,
        total_discs=1,
        title='Mr Happy',
        artist='DJ Hazard; Distorted Minds',
        album_artist='DJ Hazard; Distorted Minds',
        album='Mr Happy / Super Drunk',
        compilation=False,
        date=date(2007, 10, 8),
        label='Playaz Recordings',
        isrc='PLAYAZ002',
        resources=[
            Resource(
                codec='ogg',
                bitrate='320',
                sample_rate='44100',
                path=uuid4().hex),
            Resource(
                codec='mp3',
                bitrate='192',
                sample_rate='44100',
                path=uuid4().hex)
            ]
         )

    with db.get_session() as session:
        print("Adding:", track)
        session.add(track)

    with db.get_session() as session:
        res1 = track.resources[0]
        res2 = track.resources[1]
        print("Removing resources:", res1, res2)
        session.delete(res1)
        session.delete(res2)

    with db.get_session() as session:
        print("Checking...")
        track_ = db.get_track_by_uuid(session, track.uuid)
        if track_ is None:
            print("Track removed")
        else:
            print("Track NOT removed")
        for res in track.resources:
            res_ = db.get_resource_by_path(session, res.path)
            if res_ is None:
                print("Resource removed")


if __name__ == '__main__':
    db = Database()
    test_insert(db)
