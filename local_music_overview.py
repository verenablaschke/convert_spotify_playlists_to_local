import os
from tinytag import TinyTag

local_music_dir = "C:\\Users\\vebl-laptop\\Music"
out_file = "./music_overview.tsv"

# Incomplete(!) list of audio formats.
music_formats = ["flac", "mp3", "m4a", "ogg", "wav"]

music_files = []
for subdir, dirs, files in os.walk(local_music_dir):
    for file in files:
        if file.split(".")[-1] in music_formats:
            music_files.append(os.path.join(subdir, file))
        else:
            print("Skipping (did not recognize file format)",
                  os.path.join(subdir, file))
print("Files found:", len(music_files))

with open(out_file, "w", encoding="utf8") as f:
    for file in music_files:
        metadata = TinyTag.get(file)
        title = metadata.title if metadata.title else ""
        artist = metadata.artist if metadata.artist else ""
        album = metadata.album if metadata.album else ""
        if not (title and artist and album):
            # The follow-up script won't work properly if title or artist
            # metadata is missing!
            print(f"Missing metadata for {file}: {title}, {artist}, {album}")
        f.write(title + "\t" + artist + "\t" + album + "\t" + file + "\n")
