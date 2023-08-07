import random

from pyrogram import Client

import csv
import json


# Read CSV file
with open("tracks.csv", encoding='utf-8') as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    # next(reader, None)  # skip the headers
    tracksDB = [row for row in reader]

tracksDB.pop(0)
# print(data_read[100])
# print(data_read[200])

# нужно только для первого использования


with open("config.txt", encoding="utf-8") as configFile:
    config = json.load(configFile)

app = Client("my_account", api_id=config["api_id"], api_hash=config["api_hash"])


async def main():
    async with app:
        row = tracksDB[random.randrange(len(tracksDB))]
        print(row)
        tracksStr = row[0] + " " + row[2]
        print(tracksStr)
        bot_results = await app.get_inline_bot_results(
            "murglar_bot",
            query=tracksStr
        )

        await app.send_inline_bot_result(
            "me", bot_results.query_id,
            bot_results.results[0].id)


app.run(main())
