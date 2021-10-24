import os
from typing import Optional

from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.metadata import EpisodeId
from tqdm import tqdm

from const import NAME, ERROR, SHOW, ITEMS, ID, ROOT_PODCAST_PATH, CHUNK_SIZE
from utils import sanitize_data, create_download_directory, MusicFormat
from zspotify import ZSpotify


EPISODE_INFO_URL = 'https://api.spotify.com/v1/episodes'
SHOWS_URL = 'https://api.spotify.com/v1/shows'


def get_episode_info(episode_id_str) -> tuple[Optional[str], Optional[str]]:
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

        download_directory = os.path.dirname(__file__) + ZSpotify.get_config(ROOT_PODCAST_PATH) + extra_paths
        create_download_directory(download_directory)

        total_size = stream.input_stream.size
        with open(download_directory + filename + MusicFormat.OGG.value,
                  'wb') as file, tqdm(
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