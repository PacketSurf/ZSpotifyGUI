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
import subprocess
from const import TRACKS, ALBUM, NAME, ITEMS, DISC_NUMBER, TRACK_NUMBER, IS_PLAYABLE, ARTISTS, IMAGES, URL, \
    RELEASE_DATE, ID, TRACKS_URL, SAVED_TRACKS_URL, TRACK_STATS_URL, CODEC_MAP, EXT_MAP, DURATION_MS
from termoutput import Printer, PrintChannel
from utils import fix_filename, conv_artist_format, set_audio_tags, set_music_thumbnail, create_download_directory, \
    get_directory_song_ids, add_to_directory_song_ids, get_previously_downloaded, add_to_archive
from zspotify import ZSpotify
from config import Config

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
def download_track(track_id: str, extra_keys='', prefix=False, prefix_value='', disable_progressbar=False, progress_callback=None, mode: str="single") -> None:
    """ Downloads raw song audio from Spotify """
    try:

        logger.info(f"Initialising download {track_id}.")
        (artists, album_name, name, image_url, release_year, disc_number,
         track_number, scraped_song_id, is_playable, duration_ms) = get_song_info(track_id)
        logger.info(f"Scraped track info.")

        song_name = fix_filename(artists[0]) + ' - ' + fix_filename(name)

        output_template = Config.get_output(mode)

        for k in extra_keys:
            output_template = output_template.replace("{"+k+"}", fix_filename(extra_keys[k]))

        output_template = output_template.replace("{artist}", fix_filename(artists[0]))
        output_template = output_template.replace("{album}", fix_filename(album_name))
        output_template = output_template.replace("{song_name}", fix_filename(name))
        output_template = output_template.replace("{release_year}", fix_filename(release_year))
        output_template = output_template.replace("{disc_number}", fix_filename(disc_number))
        output_template = output_template.replace("{track_number}", fix_filename(track_number))
        output_template = output_template.replace("{id}", fix_filename(scraped_song_id))
        output_template = output_template.replace("{track_id}", fix_filename(track_id))
        output_template = output_template.replace("{ext}", EXT_MAP.get(Config.get_download_format().lower()))
        filename = os.path.join(os.path.dirname(__file__), Config.get_root_path(), output_template)
        filedir = os.path.dirname(filename)

        check_name = os.path.isfile(filename) and os.path.getsize(filename)
        check_id = scraped_song_id in get_directory_song_ids(filedir)
        check_all_time = scraped_song_id in get_previously_downloaded()

        # a song with the same name is installed
        if not check_id and check_name:
            c = len([file for file in os.listdir(filedir) if re.search(f'^{filename}_', str(file))]) + 1

            fname = os.path.splitext(os.path.basename(filename))[0]
            ext = os.path.splitext(os.path.basename(filename))[1]

            filename = os.path.join(filedir, f'{fname}_{c}{ext}')

    except Exception as e:
        logger.error(e)
        Printer.print(PrintChannel.ERRORS, '###   SKIPPING SONG - FAILED TO QUERY METADATA   ###')
        Printer.print(PrintChannel.ERRORS, str(e) + "\n")
        return DownloadStatus.FAILED
    else:
        try:
            logger.info(f"Starting Download: {output_template}")
            if not is_playable:
                Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG IS UNAVAILABLE)   ###' + "\n")
                logger.info('\n### SKIPPING: SONG IS UNAVAILABLE')
                return DownloadStatus.SKIPPED
            else:
                if check_id and check_name and Config.get_skip_existing_files():
                    Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG ALREADY EXISTS)   ###' + "\n")
                    logger.info('\n### SKIPPING: SONG ALREADY EXISTS')
                    return DownloadStatus.SKIPPED

                elif check_all_time and Config.get_skip_previously_downloaded():
                    Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG ALREADY DOWNLOADED ONCE)   ###' + "\n")
                    logger.info('\n### SKIPPING: SONG ALREADY DOWNLOADED ONCE')
                    return DownloadStatus.SKIPPED

                else:
                    if track_id != scraped_song_id:
                        track_id = scraped_song_id
                    track_id = TrackId.from_base62(track_id)
                    stream = ZSpotify.get_content_stream(
                        track_id, ZSpotify.DOWNLOAD_QUALITY)
                    create_download_directory(filedir)
                    total_size = stream.input_stream.size
                    downloaded = 0
                    total = 0
                    with open(filename, 'wb') as file, Printer.progress(
                            desc=song_name,
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            disable=disable_progressbar
                    ) as p_bar:
                        chunk_size = Config.get_chunk_size()
                        pause = duration_ms / chunk_size
                        for chunk in range(int(total_size /chunk_size) + 1):
                            data = stream.input_stream.stream().read(chunk_size)
                            dl_amount = file.write(data)
                            p_bar.update(dl_amount)
                            downloaded += dl_amount
                            if progress_callback:
                                progress_callback(downloaded/total_size)
                            if Config.get_download_real_time():
                                logger.info(f"Sleeping for real time download: {pause}s")
                                time.sleep(pause)

                    convert_audio_format(filename)
                    logger.info("Setting track metadata.")
                    set_audio_tags(filename, conv_artist_format(artists), name, album_name,
                                release_year, disc_number, track_number, spotify_id=scraped_song_id, img=image_url)
                    logger.info("Setting track thumbnail.")
                    set_music_thumbnail(filename, image_url)

                    Printer.print(PrintChannel.DOWNLOADS, f'###   Downloaded "{song_name}" to "{os.path.relpath(filename, os.path.dirname(__file__))}"   ###' + "\n")

                    # add song id to archive file
                    if Config.get_skip_previously_downloaded():
                        add_to_archive(scraped_song_id, os.path.basename(filename), artists[0], name)
                    # add song id to download directory's .song_ids file
                    if not check_id:
                        add_to_directory_song_ids(filedir, scraped_song_id, os.path.basename(filename), artists[0], name)

                    if not Config.get_anti_ban_wait_time():
                        duration = Config.get_anti_ban_wait_time()
                        time.sleep(duration)
                        logger.info(f"Sleeping for anti ban time: {duration}s")

                    return DownloadStatus.SUCCESS
        except Exception as e:
            Printer.print(PrintChannel.ERRORS, '###   SKIPPING: ' + song_name + ' (GENERAL DOWNLOAD ERROR)   ###')
            Printer.print(PrintChannel.ERRORS, str(e) + "\n")
            logger.error(f'###SKIPPING: GENERAL DOWNLOAD ERROR: {str(e)}')
            if os.path.exists(filename):
                os.remove(filename)
            return DownloadStatus.FAILED


def convert_audio_format(filename) -> None:
    """ Converts raw audio into playable file """
    download_format = Config.get_download_format().lower()
    logger.info(f"Converting downloaded file format to: {download_format}")
    temp_filename = f'{os.path.splitext(filename)[0]}.tmp'
    os.replace(filename, temp_filename)
    file_codec = CODEC_MAP.get(download_format, 'copy')
    if file_codec != 'copy':
        bitrate = Config.get_bitrate()
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
