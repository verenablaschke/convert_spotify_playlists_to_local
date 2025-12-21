import json
from pathlib import Path

# As downloaded from the Spotify GDPR export
spotify_playlist_json = "./Playlist1.json.json"

out_dir = "./playlists_spotify"

with open(spotify_playlist_json, encoding="utf8") as f:
    data = json.load(f)

forbidden_file_chars = "/\\<>:\"|?*"
name2tracks = {}
for playlist in data["playlists"]:
    name = playlist["name"]

    # Make sure the playlist name can be used
    # as a filename, and that we don't have duplicates.
    # Not especially pretty, based on the assumption
    # that this shouldn't happen very much (and should
    # be cleaned up manually anyway.
    for char in forbidden_file_chars:
        name = name.replace(char, " ")
    name = name.strip()
    while name in name2tracks:
        name += "_"
    print(playlist["name"], "->", name)

    songs = []
    for song in playlist["items"]:
        if song["track"]:
            songs.append(
                (song["track"]["trackName"], song["track"]["artistName"],
                 song["track"]["albumName"]))
        elif song["localTrack"]:
            # song from local (non-Spotify) file
            uri = song["localTrack"]["uri"]
            # format: spotify:local:[artist]:[album]:[title]:[length?]
            # spaces are replaced with +
            uri = uri.replace("+", " ")
            _, _, artist, album, title, _ = uri.split(":")
            songs.append((title, artist, album))
    name2tracks[name] = songs

Path(out_dir).mkdir(parents=True, exist_ok=True)

for name in name2tracks:
    with open(out_dir + "/" + name + ".tsv", "w", encoding="utf8") as f:
        for title, artist, album in name2tracks[name]:
            f.write(title + "\t" + artist + "\t" + album + "\n")
