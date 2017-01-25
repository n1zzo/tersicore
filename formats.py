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


def parse(field_name, dictionary):
    value = dictionary.get(field_name, None)
    if value is not None:
        return value[0]
    return value


def parse_resource(res, path):
    media = mutagen.File(path)

    res.path = path
    res.codec = FORMATS[type(media)]['pretty_name']
    res.sample_rate = media.info.sample_rate
    res.bitrate = media.info.bitrate

    res.track.track_number = parse('tracknumber', media.tags)
    res.track.total_tracks = parse('totaltracks', media.tags)
    res.track.disc_number = parse('discnumber', media.tags)
    res.track.total_discs = parse('totaldiscs', media.tags)
    res.track.label = parse('organization', media.tags)
    res.track.title = parse('title', media.tags)
    res.track.artist = parse('artist', media.tags)
    res.track.album = parse('album', media.tags)
    res.track.compilation = False
    res.track.date = date(int(parse('date', media.tags)), 1, 1)
    res.track.isrc = parse('isrc', media.tags)

    if res.codec == 'mp3':
        res.track.album_artist = parse('albumartist', media.tags)
    elif res.codec == 'ogg_vorbis':
        res.track.album_artist = parse('ensemble', media.tags)
    elif res.codec == 'flac':
        res.track.album_artist = parse('albumartist', media.tags)
