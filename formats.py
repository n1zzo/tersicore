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

    res.track.track_number = media.tags['tracknumber']
    res.track.total_tracks = media.tags['totaltracks']
    res.track.disc_number = media.tags['discnumber']
    res.track.total_discs = media.tags['totaldiscs']
    res.track.label = media.tags.get('organization', None)
    res.track.title = media.tags['title']
    res.track.artist = media.tags['artist']
    res.track.album = media.tags['album']
    res.track.compilation = False
    res.track.date = date(int(media.tags['date'][0]), 1, 1)
    res.track.isrc = media.tags['isrc']

    if res.codec == 'mp3':
        res.track.album_artist = media.tags['albumartist']
    elif res.codec == 'ogg_vorbis':
        res.track.album_artist = media.tags['ensemble']
    elif res.codec == 'flac':
        res.track.album_artist = media.tags['albumartist']

       
