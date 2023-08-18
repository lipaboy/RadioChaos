import csv


with open("tracks.csv", encoding='utf-8') as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    # next(reader, None)  # skip the headers
    tracksDB = [row for row in reader]

tracksDB.pop(0)

with open('tracksless.txt', mode="w", encoding='utf-8') as outFile:
    for row in tracksDB:
        groupName = row[0].strip()
        songName = row[2].strip()
        if len(groupName) > 0 and len(songName) > 0:
            lessData = groupName + "\n" + songName + "\n"
            outFile.write(lessData)
        else:
            print(groupName + " : " + songName)
    outFile.close()
