![Stars](https://img.shields.io/github/stars/Footsiefat/zspotify.svg)
![Forks](https://img.shields.io/github/forks/Footsiefat/zspotify.svg)
![Size](https://img.shields.io/github/repo-size/Footsiefat/zspotify)
# ZSpotify

### A Spotify downloader needing only a python interpreter and ffmpeg.
<p align="center">
  <img src="https://user-images.githubusercontent.com/12180913/138040605-c9d46e45-3830-4a4b-a7ac-c56bb0d76335.png">
</p>

[Discord Server](https://discord.gg/skVNQKtyFq) - [Matrix Server](https://matrix.to/#/#zspotify:matrix.org) - [Gitea Mirror](https://git.robinsmediateam.dev/Footsiefat/zspotify)
```
Requirements:

Binaries

- Python 3.8 or greater
- ffmpeg*

Python packages:

- pip install -r requirements.txt

```

\*ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries from [ffmpeg.org](https://ffmpeg.org) and placing them in your %PATH% in Windows.

```
Command line usage:
  python zspotify.py                              Loads search prompt to find then download a specific track, album or playlist
  python zspotify.py <track/album/playlist/episode url>   Downloads the track, album, playlist or podcast episode specified as a command line argument

Extra command line options:
  -p, --playlist       Downloads a saved playlist from your account
  -ls, --liked-songs   Downloads all the liked songs from your account

Special hardcoded options:
  ROOT_PATH           Change this path if you don't like the default directory where ZSpotify saves the music
  ROOT_PODCAST_PATH   Change this path if you don't like the default directory where ZSpotify saves the podcasts

  SKIP_EXISTING_FILES Set this to False if you want ZSpotify to overwrite files with the same name rather than skipping the song

  MUSIC_FORMAT        Set this to "ogg" if you would rather that format audio over "mp3"
  RAW_AUDIO_AS_IS     Set this to True to only stream the audio to a file and do no re-encoding or post processing
  
  FORCE_PREMIUM       Set this to True if ZSpotify isn't automatically detecting that you are using a premium account
  
  ANTI_BAN_WAIT_TIME  Change this setting if the time waited between bulk downloads is too high or low
  OVERRIDE_AUTO_WAIT  Change this to True if you want to completely disable the wait between songs for faster downloads with the risk of instability
```


## **Changelog:**
**v1.9 (22 Oct 2021):**
- Added Gitea mirror for when the Spotify Glowies come to DMCA the shit out of this.
- Changed the discord server invite to a matrix server so that won't get swatted either.
- Added option to select multiple of our saved playlists to download at once.
- Added support for downloading an entire show at once.

**v1.8 (21 Oct 2021):**
- Improved podcast downloading a bit.
- Simplified the code that catches crashes while downloading.
- Cleaned up code using linter again.
- Added option to just paste a url in the search bar to download it.
- Added a small delay between downloading each track when downloading in bulk to help with downloading issues and potential bans.

**v1.7 (21 Oct 2021):**
- Rewrote README.md to look a lot more professional.
- Added patch to fix edge case crash when downloading liked songs.
- Made premium account check a lot more reliable.
- Added experimental podcast support for specific episodes!

**v1.6 (20 Oct 2021):**
- Added Pillow to requirements.txt.
- Removed websocket-client from requirements.txt because librespot-python added it to their dependency list.
- Made it hide your password when you type it in.
- Added manual override to force premium quality if zspotify cannot auto detect it.
- Added option to just download the raw audio with no re-encoding at all.
- Added Shebang line so it runs smoother on Linux.
- Made it download the entire track at once now so it is more efficient and fixed a bug users encountered.

**v1.5 (19 Oct 2021):**
- Made downloading a lot more efficient and probably faster.
- Made the sanitizer more efficient.
- Formatted and linted all the code.

**v1.4 (19 Oct 2021):**
- Added option to encode the downloaded tracks in the "ogg" format rather than "mp3".
- Added small improvement to sanitation function so it catches another edge case.

**v1.3 (19 Oct 2021):**
- Added auto detection about if the current account is premium or not. If it is a premium account it automatically sets the quality to VERY_HIGH and otherwise HIGH if we are using a free account.
- Fixed conversion function so it now exports to the correct bitrate.
- Added sanitation to playlist names to help catch an edge case crash.
- Added option to download all your liked songs into a sub-folder.

**v1.2 (18 Oct 2021):**
- Added .gitignore.
- Replaced dependency list in README.md with a proper requirements.txt file.
- Improved the readability of README.md.

**v1.1 (16 Oct 2021):**
- Added try/except to help catch crashes where a very few specific tracks would crash either the downloading or conversion part.

**v1.0 (14 Oct 2021):**
- Adjusted some functions so it runs again with the newer version of librespot-python.
- Improved my sanitization function so it catches more edge cases.
- Fixed an issue where sometimes spotify wouldn't provide a song id for a track we are trying to download. It will now detect and skip these invalid tracks.
- Added additional check for tracks that cannot be "played" due to licence(and similar) issues. These tracks will be skipped.

**v0.9 (13 Oct 2021):**
- Initial upload, needs adjustments to get working again after backend rewrite.
