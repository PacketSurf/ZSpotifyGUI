import os
from typing import Optional, Tuple

from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.metadata import EpisodeId

from const import (ERROR, ID, ITEMS, NAME, SHOW)
from termoutput import PrintChannel, Printer
from utils import create_download_directory, fix_filename
from zspotify import ZSpotify
from config import Config

EPISODE_INFO_URL = 'https://api.spotify.com/v1/episodes'
SHOWS_URL = 'https://api.spotify.com/v1/shows'


def get_episode_info(episode_id_str) -> Tuple[Optional[str], Optional[str]]:
    (raw, info) = ZSpotify.invoke_url(f'{EPISODE_INFO_URL}/{episode_id_str}')
    if ERROR in info:
        return None, None
    return fix_filename(info[SHOW][NAME]), fix_filename(info[NAME])


def get_show_episodes(show_id_str) -> list:
    episodes = []
    offset = 0
    limit = 50

    while True:
        resp = ZSpotify.invoke_url_with_params(
            f'{SHOWS_URL}/{show_id_str}/episodes', limit=limit, offset=offset)
        offset += limit
        for episode in resp[ITEMS]:
            episodes.append(episode[ID])
        if len(resp[ITEMS]) < limit:
            break

    return episodes


def download_podcast_directly(url, filename):
    import functools
    import pathlib
    import shutil
    import requests
    from tqdm.auto import tqdm

    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(
            f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get('Content-Length', 0))

    path = pathlib.Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    r.raw.read = functools.partial(
        r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)

    return path


def download_episode(episode_id) -> None:
    podcast_name, episode_name = get_episode_info(episode_id)

    extra_paths = podcast_name + '/'

    if podcast_name is None:
        Printer.print(PrintChannel.ERRORS, '###   SKIPPING: (EPISODE NOT FOUND)   ###')
    else:
        filename = podcast_name + ' - ' + episode_name

        direct_download_url = ZSpotify.invoke_url(
            'https://api-partner.spotify.com/pathfinder/v1/query?operationName=getEpisode&variables={"uri":"spotify:episode:' + episode_id + '"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"224ba0fd89fcfdfb3a15fa2d82a6112d3f4e2ac88fba5c6713de04d1b72cf482"}}')["data"]["episode"]["audio"]["items"][-1]["url"]

        download_directory = os.path.join(Config.get_root_podcast_path(), extra_paths)
        download_directory = os.path.realpath(download_directory)
        create_download_directory(download_directory)

        if "anon-podcast.scdn.co" in direct_download_url:
            episode_id = EpisodeId.from_base62(episode_id)
            stream = ZSpotify.get_content_stream(
                episode_id, ZSpotify.DOWNLOAD_QUALITY)

            total_size = stream.input_stream.size

            filepath = os.path.join(download_directory, f"{filename}.ogg")
            if (
                os.path.isfile(filepath)
                and os.path.getsize(filepath) == total_size
                and Config.get_skip_existing_files()
            ):
                Printer.print(PrintChannel.SKIPS, "\n###   SKIPPING: " + podcast_name + " - " + episode_name + " (EPISODE ALREADY EXISTS)   ###")
                return

            with open(filepath, 'wb') as file, Printer.progress(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024
            ) as bar:
                for _ in range(int(total_size / Config.get_chunk_size()) + 1):
                    bar.update(file.write(
                        stream.input_stream.stream().read(Config.get_chunk_size())))
        else:
            filepath = os.path.join(download_directory, f"{filename}.mp3")
            download_podcast_directly(direct_download_url, filepath)

        # convert_audio_format(ROOT_PODCAST_PATH +
        #                     extra_paths + filename + '.ogg')
