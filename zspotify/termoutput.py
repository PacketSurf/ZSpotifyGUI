from enum import Enum
from tqdm import tqdm

from config import PRINT_SPLASH, PRINT_SKIPS, PRINT_DOWNLOAD_PROGRESS, PRINT_ERRORS, PRINT_DOWNLOADS
from zspotify import ZSpotify


class PrintChannel(Enum):
    SPLASH = PRINT_SPLASH
    SKIPS = PRINT_SKIPS
    DOWNLOAD_PROGRESS = PRINT_DOWNLOAD_PROGRESS
    ERRORS = PRINT_ERRORS
    DOWNLOADS = PRINT_DOWNLOADS


class Printer:
    @staticmethod
    def print(channel: PrintChannel, msg: str) -> None:
        if ZSpotify.CONFIG.get(channel.value):
            print(msg)

    @staticmethod
    def progress(iterable=None, desc=None, total=None, unit='it', disable=False, unit_scale=False, unit_divisor=1000):
        if not ZSpotify.CONFIG.get(PrintChannel.DOWNLOAD_PROGRESS.value):
            disable = True
        return tqdm(iterable=iterable, desc=desc, total=total, disable=disable, unit=unit, unit_scale=unit_scale, unit_divisor=unit_divisor)
