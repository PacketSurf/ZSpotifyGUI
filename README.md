# zspotify
Spotify song downloader without injecting into the windows client
![image](https://user-images.githubusercontent.com/12180913/137086248-371a3d81-75b3-4d75-a90c-966549c45745.png)

```
Requirements:

Binaries

- Python 3.8 or greater
- ffmpeg*

Python packages:

- pip install -r requirements.txt

```
\*ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries from [ffmpeg.org](https://ffmpeg.org) and placing them in your %PATH% in Windows.

- Use "-p" or "--playlist" to download a saved playlist from our account
- Use "-ls" or "--liked-songs" to download all the liked songs from out account
- Supply the URL or ID of a Track/Album/Playlist as an argument to download it
- Don't supply any arguments and it will give you a search input field to find and download a specific Track/Album/Playlist via the query.

- Change the musicFormat variable in zspotify.py to "ogg" if you rather that over "mp3"

![image](https://user-images.githubusercontent.com/12180913/137824672-569d1d32-a5c5-4a5a-908c-bfd09ef256b3.png)


## **Changelog:**
**v1.4 (19 Oct 2021):**
- Added option to encode the downloaded tracks in the "ogg" format rather than "mp3".
- Added small improvement to sanitation function so it catches another edge case.

**v1.3 (19 Oct 2021):**
- Added auto detection about if the current account is premium or not. If it is a premium account it automatically sets the quality to VERY_HIGH and otherwise HIGH if we are using a free account.
- Fixed conversion function so it now exports to the correct bitrate.
- Added sanitation to playlist names to help catch an edge case crash.
- Added option to download all our liked songs into a sub-folder.

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
