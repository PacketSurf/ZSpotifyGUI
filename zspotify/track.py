import os
import re
import time
from enum import Enum
import logging
from typing import Any, Tuple, List
from librespot.audio import HaltListener
from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.audio.decoders import AudioQuality
from librespot.metadata import TrackId
from ffmpy import FFmpeg
from pydub import AudioSegment
from tqdm import tqdm
import subprocess
from const import TRACKS, ALBUM, NAME, ITEMS, DISC_NUMBER, TRACK_NUMBER, IS_PLAYABLE, ARTISTS, IMAGES, URL, \
    RELEASE_DATE, ID, TRACKS_URL, SAVED_TRACKS_URL, TRACK_STATS_URL, SPLIT_ALBUM_DISCS, ROOT_PATH, DOWNLOAD_FORMAT, \
    CHUNK_SIZE, SKIP_EXISTING_FILES, ANTI_BAN_WAIT_TIME, OVERRIDE_AUTO_WAIT, BITRATE, CODEC_MAP, EXT_MAP, DOWNLOAD_REAL_TIME, \
    SKIP_PREVIOUSLY_DOWNLOADED, DURATION_MS
from utils import fix_filename, set_audio_tags, set_music_thumbnail, create_download_directory, \
    get_directory_song_ids, add_to_directory_song_ids, get_previously_downloaded, add_to_archive
from zspotify import ZSpotify

logger = logging.getLogger(__name__)

class DownloadStatus(Enum):
    FAILED = -1
    SKIPPED = 0
    SUCCESS = 1


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


def get_song_info(song_id) -> Tuple[List[str], str, str, Any, Any, Any, Any, Any, Any, int]:
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
    duration_ms = info[TRACKS][0][DURATION_MS]

    return artists, album_name, name, image_url, release_year, disc_number, track_number, scraped_song_id, is_playable, duration_ms

def get_cover_art(song_id):
    """ Retrieves url for song cover art """
    try:
        info = ZSpotify.invoke_url(f'{TRACKS_URL}?ids={song_id}&market=from_token')
        return info[TRACKS][0][ALBUM][IMAGES][0][URL]
    except Exception as e:
        logger.error(e)
        return ""


def get_song_duration(song_id: str) -> float:
    """ Retrieves duration of song in second as is on spotify """

    resp = ZSpotify.invoke_url(f'{TRACK_STATS_URL}{song_id}')
    ms_duration = resp['duration_ms']
    duration = float(ms_duration)/1000

    return duration

def play_track(spotify_id):
    track_id = TrackId.from_base62(spotify_id)
    stream = ZSpotify.SESSION.content_feeder().load(track_id,
                                           VorbisOnlyAudioQuality(AudioQuality.HIGH),
                                           False, None)
    ffplay = subprocess.Popen(
        ["ffplay", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    while True:
        byte = stream.input_stream.stream().read(5000)
        if byte == -1:
            return
        ffplay.stdin.write(byte)

# noinspection PyBroadException
def download_track(track_id: str, extra_paths='', prefix=False, prefix_value='', disable_progressbar=False, progress_callback=None) -> None:
    """ Downloads raw song audio from Spotify """
    try:

        (artists, album_name, name, image_url, release_year, disc_number,
         track_number, scraped_song_id, is_playable, duration_ms) = get_song_info(track_id)
        logger.info(f"Initialising download {scraped_song_id}:{name} - {artists}")
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

        archive_directory = os.path.join(os.path.dirname(__file__), ZSpotify.get_config(ROOT_PATH))
        check_name = os.path.isfile(filename) and os.path.getsize(filename)
        check_id = scraped_song_id in get_directory_song_ids(download_directory)
        check_all_time = scraped_song_id in get_previously_downloaded(scraped_song_id, archive_directory)

        # a song with the same name is installed
        if not check_id and check_name:
            c = len([file for file in os.listdir(download_directory)
                     if re.search(f'^{song_name}_', file)]) + 1

            filename = os.path.join(
                download_directory, f'{song_name}_{c}.{EXT_MAP.get(ZSpotify.get_config(DOWNLOAD_FORMAT))}')


    except Exception as e:
        logger.error(e)
        print(f"matt{e}")
        print('###   SKIPPING SONG - FAILED TO QUERY METADATA   ###')
        return DownloadStatus.FAILED
    else:
        try:
            logger.info(f"Starting download {scraped_song_id}:{name} - {artists}")
            if not is_playable:
                print('\n###   SKIPPING:', song_name,
                    '(SONG IS UNAVAILABLE)   ###')
                logger.info('SONG IS UNAVAILABLE')
                return DownloadStatus.SKIPPED
            else:
                if check_id and check_name and ZSpotify.get_config(SKIP_EXISTING_FILES):
                    print('\n###   SKIPPING:', song_name,
                        '(SONG ALREADY EXISTS)   ###')
                    logger.info('SONG ALREADY EXISTS')
                    return DownloadStatus.SKIPPED

                elif check_all_time and ZSpotify.get_config(SKIP_PREVIOUSLY_DOWNLOADED):
                    print('\n###   SKIPPING:', song_name,
                        '(SONG ALREADY DOWNLOADED ONCE)   ###')
                    logger.info('SONG ALREADY DOWNLOADED ONCE')
                    return DownloadStatus.SKIPPED

                else:
                    if track_id != scraped_song_id:
                        track_id = scraped_song_id
                    track_id = TrackId.from_base62(track_id)
                    stream = ZSpotify.get_content_stream(
                        track_id, ZSpotify.DOWNLOAD_QUALITY)
                    create_download_directory(download_directory)
                    total_size = stream.input_stream.size
                    downloaded = 0
                    total = 0
                    with open(filename, 'wb') as file, tqdm(
                            desc=song_name,
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            disable=disable_progressbar
                    ) as p_bar:
                        pause = duration_ms / ZSpotify.get_config(CHUNK_SIZE)
                        for chunk in range(int(total_size / ZSpotify.get_config(CHUNK_SIZE)) + 1):
                            data = stream.input_stream.stream().read(ZSpotify.get_config(CHUNK_SIZE))
                            dl_amount = file.write(data)
                            p_bar.update(dl_amount)
                            downloaded += dl_amount
                            if progress_callback:
                                progress_callback(downloaded/total_size)
                            if ZSpotify.get_config(DOWNLOAD_REAL_TIME):
                                logger.info(f"Sleeping for real time download: {pause}s")
                                time.sleep(pause)

                    convert_audio_format(filename)
                    set_audio_tags(filename, artists, name, album_name,
                                release_year, disc_number, track_number, spotify_id=scraped_song_id)
                    set_music_thumbnail(filename, image_url)

                    # add song id to archive file
                    if ZSpotify.get_config(SKIP_PREVIOUSLY_DOWNLOADED):
                        add_to_archive(scraped_song_id, archive_directory)
                    # add song id to download directory's .song_ids file
                    if not check_id:
                        add_to_directory_song_ids(download_directory, scraped_song_id)

                    if not ZSpotify.get_config(OVERRIDE_AUTO_WAIT):
                        duration = ZSpotify.get_config(ANTI_BAN_WAIT_TIME)
                        logger.info(f"Sleeping for anti ban time: {duration}s")
                        time.sleep(duration)
                    return DownloadStatus.SUCCESS
        except Exception as e:
            print('###   SKIPPING:', song_name,
                  '(GENERAL DOWNLOAD ERROR)   ###')
            print(e)
            logger.error(e)
            if os.path.exists(filename):
                os.remove(filename)
            return DownloadStatus.FAILED


def convert_audio_format(filename) -> None:
    """ Converts raw audio into playable file """
    download_format = ZSpotify.get_config(DOWNLOAD_FORMAT).lower()
    logger.info(f"Converting downloaded file format to: {download_format}")
    temp_filename = f'{os.path.splitext(filename)[0]}.tmp'
    os.replace(filename, temp_filename)

    download_format = ZSpotify.get_config(DOWNLOAD_FORMAT).lower()
    file_codec = CODEC_MAP.get(download_format, 'copy')
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
