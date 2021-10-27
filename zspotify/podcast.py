import os
from typing import Optional, Tuple

from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.metadata import EpisodeId
from tqdm import tqdm

from const import (CHUNK_SIZE, ERROR, ID, ITEMS, NAME, ROOT_PODCAST_PATH, SHOW,
                   SKIP_EXISTING_FILES)
from utils import create_download_directory, sanitize_data
from zspotify import ZSpotify

EPISODE_INFO_URL = 'https://api.spotify.com/v1/episodes'
SHOWS_URL = 'https://api.spotify.com/v1/shows'


def get_episode_info(episode_id_str) -> Tuple[Optional[str], Optional[str]]:
    info = ZSpotify.invoke_url(f'{EPISODE_INFO_URL}/{episode_id_str}')
    if ERROR in info:
        return None, None
    return sanitize_data(info[SHOW][NAME]), sanitize_data(info[NAME])


def get_show_episodes(show_id_str) -> list:
    episodes = []
    offset = 0
    limit = 50

    while True:
        resp = ZSpotify.invoke_url_with_params(f'{SHOWS_URL}/{show_id_str}/episodes', limit=limit, offset=offset)
        offset += limit
        for episode in resp[ITEMS]:
            episodes.append(episode[ID])
        if len(resp[ITEMS]) < limit:
            break

    return episodes


def download_episode(episode_id) -> None:
    podcast_name, episode_name = get_episode_info(episode_id)

    extra_paths = podcast_name + '/'

    if podcast_name is None:
        print('###   SKIPPING: (EPISODE NOT FOUND)   ###')
    else:
        filename = podcast_name + ' - ' + episode_name

        episode_id = EpisodeId.from_base62(episode_id)
        stream = ZSpotify.get_content_stream(episode_id, ZSpotify.DOWNLOAD_QUALITY)

        download_directory = os.path.join(
            os.path.dirname(__file__),
            ZSpotify.get_config(ROOT_PODCAST_PATH),
            extra_paths,
        )
        download_directory = os.path.realpath(download_directory)
        create_download_directory(download_directory)

        total_size = stream.input_stream.size

        filepath = os.path.join(download_directory, f"{filename}.ogg")
        if (
            os.path.isfile(filepath)
            and os.path.getsize(filepath) == total_size
            and ZSpotify.get_config(SKIP_EXISTING_FILES)
        ):
            print(
                "\n###   SKIPPING:",
                podcast_name,
                "-",
                episode_name,
                "(EPISODE ALREADY EXISTS)   ###",
            )
            return

        with open(filepath, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            for _ in range(int(total_size / ZSpotify.get_config(CHUNK_SIZE)) + 1):
                bar.update(file.write(
                    stream.input_stream.stream().read(ZSpotify.get_config(CHUNK_SIZE))))

        # convert_audio_format(ROOT_PODCAST_PATH +
        #                     extra_paths + filename + '.ogg')
