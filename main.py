import io
import random

from pyrogram import Client, filters

import csv
import json
import time
from pygame import mixer  # Load the popular external library
from pyrogram.types import InputPhoneContact

start = time.time()
trackDB = []
with open("tracksless.txt", encoding='utf-8') as tracksFile:
    while True:
        groupName = tracksFile.readline().strip()
        if len(groupName) <= 0:
            break
        songName = tracksFile.readline().strip()
        if len(songName) <= 0:
            break
        trackRow = (groupName, songName)
        trackDB.append(trackRow)

# print((time.time() - start) * 1000)


with open("config.txt", encoding="utf-8") as configFile:
    config = json.load(configFile)

app = Client("my_account", api_id=config["api_id"], api_hash=config["api_hash"])


async def main():
    async with app:
        row = trackDB[random.randrange(len(trackDB))]
        tracksStr = row[0] + " " + row[1]
        print(tracksStr)
        bot_results = await app.get_inline_bot_results(
            "murglar_bot",
            query=tracksStr
        )

        await app.send_inline_bot_result(
            "me", bot_results.query_id,
            bot_results.results[0].id)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


@app.on_message(filters.me)
async def my_handler(client, message):
    print("start downloading")
    file = await app.download_media(message, progress=progress, in_memory=True)
    print("finish downloading")

    # print(file)

    mixer.init()
    # mixer.music.load(file)
    mixer.music.load(io.BytesIO(file.getbuffer()))
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)


app.run()
# app.run(main())


# contact_phone = '+79538571643'
#
# contacts = await app.get_contacts()
# print(contacts)
#
# for contact in contacts:
#     if contact.phone_number == contact_phone:
#         await app.send_message(contact.username, 'text')
