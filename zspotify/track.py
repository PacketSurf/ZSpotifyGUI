import os
import time
from typing import Any, Tuple, List

from librespot.audio.decoders import AudioQuality
from librespot.metadata import TrackId
from ffmpy import FFmpeg
from pydub import AudioSegment
from tqdm import tqdm

from const import TRACKS, ALBUM, NAME, ITEMS, DISC_NUMBER, TRACK_NUMBER, IS_PLAYABLE, ARTISTS, IMAGES, URL, \
    RELEASE_DATE, ID, TRACKS_URL, SAVED_TRACKS_URL, SPLIT_ALBUM_DISCS, ROOT_PATH, DOWNLOAD_FORMAT, CHUNK_SIZE, \
    SKIP_EXISTING_FILES, ANTI_BAN_WAIT_TIME, OVERRIDE_AUTO_WAIT, BITRATE, CODEC_MAP, EXT_MAP, DOWNLOAD_REAL_TIME
from utils import fix_filename, set_audio_tags, set_music_thumbnail, create_download_directory
from zspotify import ZSpotify


def get_saved_tracks() -> list:
    """ Returns user's saved tracks """
    songs = []
    offset = 0
    limit = 50

    while True:
        resp = ZSpotify.invoke_url_with_params(
            SAVED_TRACKS_URL, limit=limit, offset=offset)
        offset += limit
        songs.extend(resp[ITEMS])
        if len(resp[ITEMS]) < limit:
            break

    return songs


def get_song_info(song_id) -> Tuple[List[str], str, str, Any, Any, Any, Any, Any, Any]:
    """ Retrieves metadata for downloaded songs """
    info = ZSpotify.invoke_url(f'{TRACKS_URL}?ids={song_id}&market=from_token')

    artists = []
    for data in info[TRACKS][0][ARTISTS]:
        artists.append(data[NAME])
    album_name = info[TRACKS][0][ALBUM][NAME]
    name = info[TRACKS][0][NAME]
    image_url = info[TRACKS][0][ALBUM][IMAGES][0][URL]
    release_year = info[TRACKS][0][ALBUM][RELEASE_DATE].split('-')[0]
    disc_number = info[TRACKS][0][DISC_NUMBER]
    track_number = info[TRACKS][0][TRACK_NUMBER]
    scraped_song_id = info[TRACKS][0][ID]
    is_playable = info[TRACKS][0][IS_PLAYABLE]

    return artists, album_name, name, image_url, release_year, disc_number, track_number, scraped_song_id, is_playable


# noinspection PyBroadException
def download_track(track_id: str, extra_paths='', prefix=False, prefix_value='', disable_progressbar=False) -> None:
    """ Downloads raw song audio from Spotify """

    try:
        (artists, album_name, name, image_url, release_year, disc_number,
         track_number, scraped_song_id, is_playable) = get_song_info(track_id)

        if ZSpotify.get_config(SPLIT_ALBUM_DISCS):
            download_directory = os.path.join(os.path.dirname(
                __file__), ZSpotify.get_config(ROOT_PATH), extra_paths, f'Disc {disc_number}')
        else:
            download_directory = os.path.join(os.path.dirname(
                __file__), ZSpotify.get_config(ROOT_PATH), extra_paths)

        song_name = fix_filename(artists[0]) + ' - ' + fix_filename(name)
        if prefix:
            song_name = f'{prefix_value.zfill(2)} - {song_name}' if prefix_value.isdigit(
            ) else f'{prefix_value} - {song_name}'

        filename = os.path.join(
            download_directory, f'{song_name}.{EXT_MAP.get(ZSpotify.get_config(DOWNLOAD_FORMAT).lower())}')

    except Exception as e:
        print('###   SKIPPING SONG - FAILED TO QUERY METADATA   ###')
        print(e)
    else:
        try:
            if not is_playable:
                print('\n###   SKIPPING:', song_name,
                    '(SONG IS UNAVAILABLE)   ###')
            else:
                if os.path.isfile(filename) and os.path.getsize(filename) and ZSpotify.get_config(SKIP_EXISTING_FILES):
                    print('\n###   SKIPPING:', song_name,
                        '(SONG ALREADY EXISTS)   ###')
                else:
                    if track_id != scraped_song_id:
                        track_id = scraped_song_id
                    track_id = TrackId.from_base62(track_id)
                    stream = ZSpotify.get_content_stream(
                        track_id, ZSpotify.DOWNLOAD_QUALITY)
                    create_download_directory(download_directory)
                    total_size = stream.input_stream.size

                    with open(filename, 'wb') as file, tqdm(
                            desc=song_name,
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            disable=disable_progressbar
                    ) as p_bar:
                        for chunk in range(int(total_size / ZSpotify.get_config(CHUNK_SIZE)) + 1):
                            data = stream.input_stream.stream().read(ZSpotify.get_config(CHUNK_SIZE))
                            if data == b'':
                                break
                            p_bar.update(file.write(data))
                            if ZSpotify.get_config(DOWNLOAD_REAL_TIME):
                                if chunk == 0:
                                    pause = get_segment_duration(p_bar)
                                if pause:
                                    time.sleep(pause)

                    convert_audio_format(filename)
                    set_audio_tags(filename, artists, name, album_name,
                                release_year, disc_number, track_number)
                    set_music_thumbnail(filename, image_url)

                    if not ZSpotify.get_config(OVERRIDE_AUTO_WAIT):
                        time.sleep(ZSpotify.get_config(ANTI_BAN_WAIT_TIME))
        except Exception as e:
            print('###   SKIPPING:', song_name,
                  '(GENERAL DOWNLOAD ERROR)   ###')
            print(e)
            if os.path.exists(filename):
                os.remove(filename)


def get_segment_duration(segment):
    """ Returns playback duration of given audio segment """
    sound = AudioSegment(
        data = segment,
        sample_width = 2,
        frame_rate = 44100,
        channels = 2
    )
    duration = len(sound) / 5000
    return duration


def convert_audio_format(filename) -> None:
    """ Converts raw audio into playable file """
    temp_filename = f'{os.path.splitext(filename)[0]}.tmp'
    os.replace(filename, temp_filename)

    download_format = ZSpotify.get_config(DOWNLOAD_FORMAT).lower()
    file_codec = CODEC_MAP.get(download_format, "copy")
    if file_codec != 'copy':
        bitrate = ZSpotify.get_config(BITRATE)
        if not bitrate:
            if ZSpotify.DOWNLOAD_QUALITY == AudioQuality.VERY_HIGH:
                bitrate = '320k'
            else:
                bitrate = '160k'
    else:
        bitrate = None

    output_params = ['-c:a', file_codec]
    if bitrate:
        output_params += ['-b:a', bitrate]

    ff_m = FFmpeg(
        global_options=['-y', '-hide_banner', '-loglevel error'],
        inputs={temp_filename: None},
        outputs={filename: output_params}
    )
    ff_m.run()
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
