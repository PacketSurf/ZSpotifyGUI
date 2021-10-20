# XSpotify

### A Spotify downloader needing only a python interpreter and ffmpeg.
<p align="center">
  <img src="https://user-images.githubusercontent.com/12180913/138040605-c9d46e45-3830-4a4b-a7ac-c56bb0d76335.png">
</p>

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
  python zspotify.py <track/album/playlist url>   Downloads the track, album or playlist specified as a command line argument

Extra command line options:

  -p, --playlist       Downloads a saved playlist from your account
  -ls, --liked-songs   Downloads all the liked songs from your account

Special hardcoded options:
  MUSIC_FORMAT      Set this to "ogg" if you would rather that format audio over "mp3"
  FORCE_PREMIUM     Set this to True if ZSpotify isn't automatically detecting that you are using a premium account
  RAW_AUDIO_AS_IS   Set this to True to only stream the audio to a file and do no re-encoding or post processing
```


## **Changelog:**
**v1.6 (20 Oct 2021):**
- Added Pillow to requirements.txt.
- Removed websocket-client from requirements.txt because librespot-python added it to their dependency list.
- Made it hide your password when you type it in.
- Added manual override to force premium quality if zspotify cannot auto detect it.
- Added option to just download the raw audio with no re-encoding at all.
- Added Shebang line so it runs smoother on Linux.
- Made it download the entire track at once now so it is more efficent and fixed a bug users encountered.

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
- Ajusted some functions so it runs again with the newer version of librespot-python.
- Improved my sanitization function so it catches more edge cases.
- Fixed an issue where sometimes spotify wouldnt provide a song id for a track we are trying to download. It will now detect and skip these invalid tracks.
- Added additional check for tracks that cannot be "played" due to licence(and similar) issues. These tracks will be skipped.

**v0.9 (13 Oct 2021):**
- Initial upload, needs adjustments to get working again after backend rewrite.
