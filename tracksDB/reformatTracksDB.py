import csv

with open("tracks.csv", encoding='utf-8') as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    # next(reader, None)  # skip the headers
    tracksDB = [row for row in reader]

tracksDB.pop(0)

attrs = ["artist", "artist_spotify_id", "name", "spotify_id",
         "duration_ms", "explicit", "popularity",
         "album_type", "album_name", 'album_spotify_id',
         'release_date', 'album_popularity', 'key', 'mode',
         'time_signature', 'acousticness',
         'danceability', 'energy', 'instrumentalness',
         'liveness', 'loudness', 'speechiness', 'valence', 'tempo']


with open('tracksless.csv', mode="w", encoding='utf-8') as outFile:
    file_writer = csv.DictWriter(outFile, delimiter=",", lineterminator="\n",
                                 fieldnames=['artist', 'songLabel', 'releaseDate'])
    file_writer.writeheader()
    for row in tracksDB:
        groupName = row[attrs.index('artist')].strip()
        songName = row[attrs.index('name')].strip()
        dateStr = row[attrs.index('release_date')].strip()
        dateStr = dateStr[:4]
        if not dateStr.isdigit():
            dateStr = "None"
        if len(groupName) > 0 and len(songName) > 0:
            file_writer.writerow({'artist': groupName,
                                  'songLabel': songName,
                                  'releaseDate': dateStr})
        else:
            print(groupName + " : " + songName)
    outFile.close()
