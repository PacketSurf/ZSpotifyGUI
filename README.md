# zspotify
Spotify song downloader without injecting into the windows client
![image](https://user-images.githubusercontent.com/12180913/137086248-371a3d81-75b3-4d75-a90c-966549c45745.png)
```
### Requirements:

Binaries

\- Python 3.8 or greater
\- ffmpeg\*

Python packages:

Install these with pip install *package name*

\- websocket-client
\- requests
\- music_tag
\- pydub
\- git+https://github.com/kokarare1212/librespot-python
```
ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries and placing them in your %PATH% in Windows.

- Use "-p" or "--playlist" to download a saved playlist from our account
- Supply the URL or ID of a Track/Album/Playlist as an argument to download it
- Don't supply any arguments and it will give you a search input field to find and download a specific Track/Album/Playlist via the query.
