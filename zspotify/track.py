import os
import time
from typing import Any, Tuple, List

from librespot.audio.decoders import AudioQuality
from librespot.metadata import TrackId
from pydub import AudioSegment
from tqdm import tqdm

from const import TRACKS, ALBUM, NAME, ITEMS, DISC_NUMBER, TRACK_NUMBER, IS_PLAYABLE, ARTISTS, IMAGES, URL, \
    RELEASE_DATE, ID, TRACKS_URL, SAVED_TRACKS_URL, SPLIT_ALBUM_DISCS, ROOT_PATH, DOWNLOAD_FORMAT, CHUNK_SIZE, \
    SKIP_EXISTING_FILES, ANTI_BAN_WAIT_TIME, OVERRIDE_AUTO_WAIT
from utils import sanitize_data, set_audio_tags, set_music_thumbnail, create_download_directory, \
    MusicFormat
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
        artists.append(sanitize_data(data[NAME]))
    album_name = sanitize_data(info[TRACKS][0][ALBUM][NAME])
    name = sanitize_data(info[TRACKS][0][NAME])
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

        song_name = artists[0] + ' - ' + name
        if prefix:
            song_name = f'{prefix_value.zfill(2)} - {song_name}' if prefix_value.isdigit(
            ) else f'{prefix_value} - {song_name}'

        filename = os.path.join(
            download_directory, f'{song_name}.{ZSpotify.get_config(DOWNLOAD_FORMAT)}')

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
                        for _ in range(int(total_size / ZSpotify.get_config(CHUNK_SIZE)) + 1):
                            p_bar.update(file.write(
                                stream.input_stream.stream().read(ZSpotify.get_config(CHUNK_SIZE))))

                    if ZSpotify.get_config(DOWNLOAD_FORMAT) == 'mp3':
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


def convert_audio_format(filename) -> None:
    """ Converts raw audio into playable mp3 """
    # print('###   CONVERTING TO ' + MUSIC_FORMAT.upper() + '   ###')
    raw_audio = AudioSegment.from_file(filename, format=MusicFormat.OGG.value,
                                       frame_rate=44100, channels=2, sample_width=2)
    if ZSpotify.DOWNLOAD_QUALITY == AudioQuality.VERY_HIGH:
        bitrate = '320k'
    else:
        bitrate = '160k'
    raw_audio.export(filename, format=ZSpotify.get_config(
        DOWNLOAD_FORMAT), bitrate=bitrate)
