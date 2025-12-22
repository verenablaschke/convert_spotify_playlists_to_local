# Converting Spotify playlists to local music playlists

Converts Spotify playlists by attempting to match the songs therein to local music files.
Produces one [M3U](https://en.wikipedia.org/wiki/M3U) per playlist.
Each M3U contains just a list of local file paths, a very simple format that many music/media players should be able to deal with.

1. Export your Spotify playlists by requesting a copy of your account data: https://www.spotify.com/us/account/privacy/. Extract the ZIP archive and look for the JSON file containing the playlist information.
2. Turn the resulting JSON into one TSV file per playlist, containing the title, artist, and album of each track (adjust the file path to the JSON file at the top of the script and the output folder as necessary):
```
python3 reformat_spotify_playlist_export.py
```
3. Get a similar TSV overview of your local music (results in `music_overview.tsv`, or change the output file path at the top of the script):
```
python3 local_music_overview.py
```
4. Convert the Spotify playlists into playlists of local files, to the extent possible. This results in one M3U file per playlist.
Again, adjust the in-/output file paths to the script at the top.
Also, set the `min_length` parameter, which determines how many (matched) songs a converted playlist needs to contain in order to be saved.
```
python3 spotify_to_m3u.py
```
5. Bye, Spotify!

Notes
- These scripts rely on the local music files having proper metadata (at least song title and artist).
- The logic for matching Spotify songs with local song files relies only on the titles and artist names at the moment, ignoring album information.
- The matching logic is optimized for my music collection and might need to be adapted for other people's collections. For details, see `spotify_to_m3u.py`.
