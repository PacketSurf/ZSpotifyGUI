# zspotify
Spotify song downloader without injecting into the windows client
![image](https://user-images.githubusercontent.com/12180913/137086248-371a3d81-75b3-4d75-a90c-966549c45745.png)
```
sudo apt install ffmpeg (For windows download the binarys and place it in %PATH%)
pip install requests
pip install music_tag
pip install pydub
pip install websocket-client
pip install git+https://github.com/kokarare1212/librespot-python
```


- Use "-p" or "--playlist" to download a saved playlist from our account
- Supply the URL or ID of a Track/Album/Playlist as an argument to download it
- Don't supply any arguments and it will give you a search input field to find and download a specific Track/Album/Playlist via the query.
