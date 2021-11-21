import os
import re
import time
from typing import Any, Tuple, List

from librespot.audio.decoders import AudioQuality
from librespot.metadata import TrackId
from ffmpy import FFmpeg
from pydub import AudioSegment

from const import TRACKS, ALBUM, NAME, ITEMS, DISC_NUMBER, TRACK_NUMBER, IS_PLAYABLE, ARTISTS, IMAGES, URL, \
    RELEASE_DATE, ID, TRACKS_URL, SAVED_TRACKS_URL, TRACK_STATS_URL, CODEC_MAP, EXT_MAP, DURATION_MS
from termoutput import Printer, PrintChannel
from utils import fix_filename, set_audio_tags, set_music_thumbnail, create_download_directory, \
    get_directory_song_ids, add_to_directory_song_ids, get_previously_downloaded, add_to_archive
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

def get_song_duration(song_id: str) -> float:
    """ Retrieves duration of song in second as is on spotify """

    resp = ZSpotify.invoke_url(f'{TRACK_STATS_URL}{song_id}')

    # get duration in miliseconds
    ms_duration = resp['duration_ms']
    # convert to seconds
    duration = float(ms_duration)/1000

    # debug
    # print(duration)
    # print(type(duration))

    return duration

# noinspection PyBroadException
def download_track(mode: str, track_id: str, extra_keys={}, disable_progressbar=False) -> None:
    """ Downloads raw song audio from Spotify """

    try:
        output_template = ZSpotify.CONFIG.get_output(mode)

        (artists, album_name, name, image_url, release_year, disc_number,
         track_number, scraped_song_id, is_playable, duration_ms) = get_song_info(track_id)

        song_name = fix_filename(artists[0]) + ' - ' + fix_filename(name)

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
        output_template = output_template.replace("{ext}", EXT_MAP.get(ZSpotify.CONFIG.get_download_format().lower()))

        filename = os.path.join(os.path.dirname(__file__), ZSpotify.CONFIG.get_root_path(), output_template)
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
        Printer.print(PrintChannel.ERRORS, '###   SKIPPING SONG - FAILED TO QUERY METADATA   ###')
        Printer.print(PrintChannel.ERRORS, str(e) + "\n")
    else:
        try:
            if not is_playable:
                Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG IS UNAVAILABLE)   ###' + "\n")
            else:
                if check_id and check_name and ZSpotify.CONFIG.get_skip_existing_files():
                    Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG ALREADY EXISTS)   ###' + "\n")

                elif check_all_time and ZSpotify.CONFIG.get_skip_previously_downloaded():
                    Printer.print(PrintChannel.SKIPS, '\n###   SKIPPING: ' + song_name + ' (SONG ALREADY DOWNLOADED ONCE)   ###' + "\n")

                else:
                    if track_id != scraped_song_id:
                        track_id = scraped_song_id
                    track_id = TrackId.from_base62(track_id)
                    stream = ZSpotify.get_content_stream(
                        track_id, ZSpotify.DOWNLOAD_QUALITY)
                    create_download_directory(filedir)
                    total_size = stream.input_stream.size

                    with open(filename, 'wb') as file, Printer.progress(
                            desc=song_name,
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            disable=disable_progressbar
                    ) as p_bar:
                        pause = duration_ms / ZSpotify.CONFIG.get_chunk_size()
                        for chunk in range(int(total_size / ZSpotify.CONFIG.get_chunk_size()) + 1):
                            data = stream.input_stream.stream().read(ZSpotify.CONFIG.get_chunk_size())
                            p_bar.update(file.write(data))
                            if ZSpotify.CONFIG.get_download_real_time():
                                time.sleep(pause)

                    convert_audio_format(filename)
                    set_audio_tags(filename, artists, name, album_name, release_year, disc_number, track_number)
                    set_music_thumbnail(filename, image_url)

                    Printer.print(PrintChannel.DOWNLOADS, f'###   Downloaded "{song_name}" to "{os.path.relpath(filename, os.path.dirname(__file__))}"   ###' + "\n")

                    # add song id to archive file
                    if ZSpotify.CONFIG.get_skip_previously_downloaded():
                        add_to_archive(scraped_song_id, os.path.basename(filename), artists[0], name)
                    # add song id to download directory's .song_ids file
                    if not check_id:
                        add_to_directory_song_ids(filedir, scraped_song_id, os.path.basename(filename), artists[0], name)

                    if not ZSpotify.CONFIG.get_anti_ban_wait_time():
                        time.sleep(ZSpotify.CONFIG.get_anti_ban_wait_time())
        except Exception as e:
            Printer.print(PrintChannel.ERRORS, '###   SKIPPING: ' + song_name + ' (GENERAL DOWNLOAD ERROR)   ###')
            Printer.print(PrintChannel.ERRORS, str(e) + "\n")
            if os.path.exists(filename):
                os.remove(filename)


def convert_audio_format(filename) -> None:
    """ Converts raw audio into playable file """
    temp_filename = f'{os.path.splitext(filename)[0]}.tmp'
    os.replace(filename, temp_filename)

    download_format = ZSpotify.CONFIG.get_download_format().lower()
    file_codec = CODEC_MAP.get(download_format, 'copy')
    if file_codec != 'copy':
        bitrate = ZSpotify.CONFIG.get_bitrate()
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
