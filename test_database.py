from log import get_logger
from database import Database, Track, Resource

from datetime import date
from uuid import uuid4


log = get_logger('test.database')


def test_insert(db):
    log.info("Starting database tests.")
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
        log.debug("Adding a new Track object to the session: %s", track)
        session.add(track)

    log.debug("Track object status after insert: %s", track)

    with db.get_session() as session:
        log.debug("Query for uuid: %s", track.uuid)
        track_ = db.get_track_by_uuid(session, track.uuid)
        track_resources = track.resources
        log.debug("Result: %s %s", track_, track_resources)

    with db.get_session() as session:
        log.debug("Query for: {title='happy', artist='hazard'}")
        tracks = db.get_tracks(session, title='happy', artist='hazard')
        log.debug("Results: %s", str([t for t in tracks]))

    with db.get_session() as session:
        log.debug("Query for: {text='happy', artist='hazard'}")
        tracks = db.get_tracks(session, text='happy', artist='hazard')
        log.debug("Results: %s", str([t for t in tracks]))

    with db.get_session() as session:
        log.debug("Removing: %s", track_)
        session.delete(track_)

    with db.get_session() as session:
        log.debug("Running checks...")
        track_ = db.get_track_by_uuid(session, track.uuid)
        if track_ is None:
            log.debug("Track with uuid %s removed", track.uuid)
        else:
            log.debug("Track with uuid %s NOT removed", track.uuid)
        for res in track.resources:
            res_ = db.get_resource_by_uuid(session, res.uuid)
            if res_ is None:
                log.debug("Resource with uuid %s removed", res.uuid)
            else:
                log.debug("Resource with uuid %s NOT removed", res.uuid)

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
        log.debug("Adding a new Track object to the session: %s", track)
        session.add(track)

    with db.get_session() as session:
        res1 = track.resources[0]
        res2 = track.resources[1]
        log.debug("Removing resources: %s %s", res1, res2)
        session.delete(res1)
        session.delete(res2)

    with db.get_session() as session:
        log.debug("Running checks...")
        track_ = db.get_track_by_uuid(session, track.uuid)
        if track_ is None:
            log.debug("Track with uuid %s removed", track.uuid)
        else:
            log.debug("Track with uuid %s NOT removed", track.uuid)
        for res in track.resources:
            res_ = db.get_resource_by_path(session, res.path)
            if res_ is None:
                log.debug("Resource with uuid %s removed", res.uuid)
            else:
                log.debug("Resource with uuid %s NOT removed", res.uuid)


if __name__ == '__main__':
    db = Database()
    test_insert(db)
