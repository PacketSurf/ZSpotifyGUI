from tqdm import tqdm
import logging
from const import ITEMS, ARTISTS, NAME, ID
from track import DownloadStatus, download_track
from termoutput import Printer
from utils import fix_filename
from zspotify import ZSpotify

ALBUM_URL = 'https://api.spotify.com/v1/albums'
ARTIST_URL = 'https://api.spotify.com/v1/artists'

logger = logging.getLogger(__name__)

def get_album_tracks(album_id):
    """ Returns album tracklist """
    songs = []
    offset = 0
    limit = 50

    while True:
        resp = ZSpotify.invoke_url_with_params(f'{ALBUM_URL}/{album_id}/tracks', limit=limit, offset=offset)
        offset += limit
        songs.extend(resp[ITEMS])
        if len(resp[ITEMS]) < limit:
            break

    return songs


def get_album_name(album_id):
    """ Returns album name """
    (raw, resp) = ZSpotify.invoke_url(f'{ALBUM_URL}/{album_id}')
    return resp[ARTISTS][0][NAME], fix_filename(resp[NAME])


def get_artist_albums(artist_id):
    """ Returns artist's albums """
    logger.info("Starting artist albums download.")
    (raw, resp) = ZSpotify.invoke_url(f'{ARTIST_URL}/{artist_id}/albums?include_groups=album%2Csingle')
    # Return a list each album's id
    album_ids = [resp[ITEMS][i][ID] for i in range(len(resp[ITEMS]))]
    # Recursive requests to get all albums including singles an EPs
    while resp['next'] is not None:
        (raw, resp) = ZSpotify.invoke_url(resp['next'])
        album_ids.extend([resp[ITEMS][i][ID] for i in range(len(resp[ITEMS]))])

    return album_ids


def download_album(album, progress_callback=None):
    """ Downloads songs from an album """

    artist, album_name = get_album_name(album)
    tracks = get_album_tracks(album)
    downloaded = 0
    one_success = False
    logger.info("Starting album download.")
    for n, track in tqdm(enumerate(tracks, start=1), unit_scale=True, unit='Song', total=len(tracks)):
        status = download_track(track[ID], mode='album', extra_keys={'album_num': str(n).zfill(2), 'artist': artist, 'album': album_name, 'album_id': album},
            disable_progressbar=True, progress_callback=progress_callback)
        if status.value == DownloadStatus.FAILED.value:
            return DownloadStatus.FAILED
        elif status.value == DownloadStatus.SUCCESS.value:
            one_success = True
        downloaded += 1
    if one_success:
        return DownloadStatus.SUCCESS
    return DownloadStatus.FAILED



def download_artist_albums(artist, progress_callback=None):
    """ Downloads albums of an artist """
    albums = get_artist_albums(artist)
    one_success = False
    for album_id in albums:
        status = download_album(album_id, progress_callback=progress_callback)
        if status.value == DownloadStatus.FAILED.value:
            return DownloadStatus.FAILED
        elif status.value == DownloadStatus.SUCCESS.value:
            one_success = True
    if one_success:
        return DownloadStatus.SUCCESS
    return DownloadStatus.FAILED
