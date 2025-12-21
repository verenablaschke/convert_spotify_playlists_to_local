import os
import re
from pathlib import Path

# Input folder (created with earlier script)
folder_spotify_tsv_playlists = "./playlists_spotify"
# Output folder (new m3u playlist files)
folder_local_playlists = "./playlists_local"
# Folder for storing log data (which songs where matched how (or not))
folder_logs = "./playlists_logs"
# How many matched(!) songs should a playlist
# contain in order to be converted?
min_length = 10


def normalize_title(title):
    title = title.lower()
    title = title.replace("(remastered)", "")
    title = re.sub("- [0-9]+ remaster", "", title)
    title = re.sub("- remastered *[0-9]*", "", title)
    title = title.replace("(original)", "")
    title = title.replace("- instrumental", "[instrumental]")
    return title.strip()


def normalize_title_fuzzy(title):
    title = title.replace(" ?", "")
    title = title.replace("?", "")
    title = title.replace("(live)", "")
    title = title.replace("[live]", "")
    title = title.replace("- live", "")
    title = title.replace("(acoustic)", "")
    title = title.replace("[acoustic]", "")
    title = title.replace("- acoustic", "")
    title = re.sub("- *[0-9a-z]* edit", "", title)
    title = re.sub("\([0-9a-z]* edit\)", "", title)
    title = re.sub("\[[0-9a-z]* edit\]", "", title)
    title = re.sub("- *[0-9a-z]* remix", "", title)
    title = re.sub("\([0-9a-z]* remix\)", "", title)
    title = re.sub("\[[0-9a-z]* remix\]", "", title)
    title = re.sub("\(from .*\)", "", title)
    title = re.sub("\[from .*\]", "", title)
    title = re.sub("\(with .*\)", "", title)
    title = re.sub("\[with .*\]", "", title)
    title = re.sub("\(feat.*\)", "", title)
    title = re.sub("\[feat.*\]", "", title)
    return title.strip()


def normalize_title_parens(title):
    title = re.sub("\(.*\)", "", title)
    title = re.sub("\[.*\]", "", title)
    title = "".join(title.split(" - ")[:-1])
    return title.strip()


def artists_match(artist1, artist2, recurse=True):
    artist1 = artist1.lower()
    artist2 = artist2.lower()
    if artist1 == artist2:
        return True
    if artist1.startswith(artist2):
        return True
    if artist2.startswith(artist1):
        return True
    if artist1.endswith(artist2):
        return True
    if artist2.endswith(artist1):
        return True
    if recurse:
        return artists_match(artist1.replace("the ", ""),
                             artist2.replace("the ", ""),
                             recurse=False)
    return False


def custom_match(title, artist):
    if title.startswith("the road to hell") and (
            "ii" in title or "2" in title):
        return title2songs["the road to hell (part ii)"][0]
    if title.startswith("the fall of the house of usher"):
        if "prelude" in title:
            return title2songs["the fall of the house of usher: i. prelude"][0]
        if "arrival" in title:
            return title2songs["the fall of the house of usher: ii. arrival"][0]
        if "intermezzo" in title:
            return title2songs["the fall of the house of usher: iii. intermezzo"][0]
        if "pavane" in title:
            return title2songs["the fall of the house of usher: iv. pavane"][0]
        if "fall" in title:
            return title2songs["the fall of the house of usher: v. fall"][0]
        else:
            return None
    if title.startswith("aquarius") and "let the sunshine in" in title:
        return title2songs["aquarius / let the sunshine in"][0]
    return None


def find_song(title, artist):
    # Direct match?
    title_found = title in title2songs
    if title_found:
        for local_song in title2songs[title]:
            if artists_match(artist, local_song[1]):
                return local_song

    # Somewhat fuzzier match?
    fuzzy_title = normalize_title_fuzzy(title)
    fuzzy_title_found = fuzzy_title in fuzzy2songs
    if fuzzy_title_found:
        for local_song in fuzzy2songs[fuzzy_title]:
            if artists_match(artist, local_song[1]):
                return local_song

    # Ignore parentheticals
    fuzzy_title_no_parens = normalize_title_parens(fuzzy_title)
    fuzzy_title_no_parens_found = fuzzy_title_no_parens in fuzzy_no_parens2songs
    if fuzzy_title_no_parens_found:
        for local_song in fuzzy_no_parens2songs[fuzzy_title_no_parens]:
            if artists_match(artist, local_song[1]):
                return local_song

    custom_match_song = custom_match(title, artist)
    if custom_match_song:
        return custom_match_song

    # For debugging:
#     print(title, title_found, artist,
#           fuzzy_title, fuzzy_title_found,
#           fuzzy_title_no_parens, fuzzy_title_no_parens_found)
    return None


title2songs = {}
fuzzy2songs = {}
fuzzy_no_parens2songs = {}
with open("./music_overview.tsv", encoding="utf8") as f:
    for line in f:
        song = line.strip().split("\t")
        title = normalize_title(song[0])
        if title in title2songs:
            title2songs[title].append(song)
        else:
            title2songs[title] = [song]
        title_fuzzy = normalize_title_fuzzy(title)
        if title_fuzzy in fuzzy2songs:
            fuzzy2songs[title_fuzzy].append(song)
        else:
            fuzzy2songs[title_fuzzy] = [song]
        title_fuzzy_no_parens = normalize_title_parens(title_fuzzy)
        if title_fuzzy_no_parens in fuzzy_no_parens2songs:
            fuzzy_no_parens2songs[title_fuzzy_no_parens].append(song)
        else:
            fuzzy_no_parens2songs[title_fuzzy_no_parens] = [song]


Path(folder_local_playlists).mkdir(parents=True, exist_ok=True)
Path(folder_logs).mkdir(parents=True, exist_ok=True)

playlist_coverages = []
for subdir, dirs, files in os.walk(folder_spotify_tsv_playlists):
    for file in files:
        if not file.endswith(".tsv"):
            continue
        found = 0
        not_found = 0
        songs_found = []
        with open(os.path.join(subdir, file), encoding="utf8") as f_in:
            with open(os.path.join(folder_logs, file), "w", encoding="utf8") as f_out:
                f_out.write("Title_Spotify\tArtist_Spotify\tAlbum_Spotify\t")
                f_out.write("Title_Local\tArtist_Local\tAlbum_Local\tPath_Local\n")
                for line in f_in:
                    song = line.strip().split("\t")
                    title = normalize_title(song[0])
                    try:
                        artist = song[1]
                    except IndexError:
                        artist = ""
                    f_out.write(title + "\t" + artist + "\t")
                    if len(song) > 2:
                        f_out.write(song[2])
                    f_out.write("\t")
                    matched = find_song(title, artist)
                    if matched:
                        found += 1
                        songs_found.append(matched[-1])  # just the path
                        f_out.write("\t".join(matched))
                    else:
                        not_found += 1
                        f_out.write("\t\t\t")
                    f_out.write("\n")
        total = found + not_found
        print(file[:-4], found, "/", total, found >= min_length)
        if total >= min_length:
            with open(os.path.join(folder_local_playlists, file[:-3] + "m3u"),
                      "w", encoding="utf8") as f_out:
                for path in songs_found:
                    f_out.write(path + "\n")
        playlist_coverages.append((found / total, total, found, file[:-4]))

with open(os.path.join(folder_logs, "_STATS.tsv"),
          "w", encoding="utf8") as f:
    f.write("Playlist\t# matched\t# original\n")
    for _, total, found, name in sorted(playlist_coverages, key=lambda x: x[3]):
        f.write(f"{name}\t{found}\t{total}\n")

print("DONE!")
print("---------")
print("Sorted by coverage (only playlists with min. length):")
for perc, total, found, name in sorted(
        playlist_coverages, reverse=True):
    if found >= min_length:
        print(f"{name}\t{str(int(100 * perc))}% ({found}/{total})")
