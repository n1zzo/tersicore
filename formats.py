from datetime import date
from fnmatch import fnmatch

import mutagen
import mutagen.id3
import mutagen.oggvorbis
import mutagen.flac


FORMATS = {
    mutagen.id3.ID3FileType: {
        'pretty_name': 'mp3',
        'extensions': ['mp3']
        },
    mutagen.oggvorbis.OggVorbis: {
        'pretty_name': 'ogg_vorbis',
        'extensions': ['ogg', 'oga']
        },
    mutagen.flac.FLAC: {
        'pretty_name': 'flac',
        'extensions': ['flac']
        }
    }

FORMATS_GLOB = ["*.{}".format(ext)
                for k, v in FORMATS.items()
                for ext in v['extensions']
                ]


def glob_match(path, globs):
    return any(fnmatch(path, glob) for glob in globs)


def parse_resource(res, path):
    media = mutagen.File(path)

    res.path = path
    res.codec = FORMATS[type(media)]['pretty_name']
    res.sample_rate = media.info.sample_rate
    res.bitrate = media.info.bitrate

    res.track.track_number = media.tags.get('tracknumber', None)[0]
    res.track.total_tracks = media.tags.get('totaltracks', None)[0]
    res.track.disc_number = media.tags.get('discnumber', None)[0]
    res.track.total_discs = media.tags.get('totaldiscs', None)[0]
    res.track.label = media.tags.get('organization', None)[0]
    res.track.title = media.tags.get('title', None)[0]
    res.track.artist = media.tags.get('artist', None)[0]
    res.track.album = media.tags.get('album', None)[0]
    res.track.compilation = False
    res.track.date = date(int(media.tags.get('date', None)[0]), 1, 1)
    res.track.isrc = media.tags.get('isrc', None)[0]

    if res.codec == 'mp3':
        res.track.album_artist = media.tags.get('albumartist', None)[0]
    elif res.codec == 'ogg_vorbis':
        res.track.album_artist = media.tags.get('ensemble', None)[0]
    elif res.codec == 'flac':
        res.track.album_artist = media.tags.get('albumartist', None)[0]
