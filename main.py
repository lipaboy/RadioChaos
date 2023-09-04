import asyncio
import io
import random

import pyrogram.types
from pyrogram import Client, filters

import json
import time
from pygame import mixer  # Load the popular external library
from pyrogram.types import InputPhoneContact, InputMediaAudio


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


with open("config.txt", encoding="utf-8") as configFile:
    config = json.load(configFile)

app = Client("my_account", api_id=config["api_id"], api_hash=config["api_hash"])


async def get_last_message():
    async for message in app.get_chat_history("me", limit=1, offset_id=-1):
        return message


async def downloadTrackFromMessage(message):
    print("start downloading")
    file = await app.download_media(message, progress=progress, in_memory=True)
    print("finish downloading")
    return file


def playSongFromFile(file):
    mixer.init()
    mixer.music.load(io.BytesIO(file.getbuffer()))
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)


async def playRandomTrack():
    async with app:
        global start

        print(time.time() - start)
        row = trackDB[random.randrange(len(trackDB))]
        tracksStr = row[0] + " " + row[1]
        # print(tracksStr)

        start = time.time()
        bot_results = await app.get_inline_bot_results(
            "murglar_bot",
            query=tracksStr
        )

        await app.send_inline_bot_result(
            "me", bot_results.query_id,
            bot_results.results[0].id)
        print(time.time() - start)

        trackMessage = await get_last_message()
        while trackMessage.reply_markup is not None:
            await asyncio.sleep(1)
            trackMessage = await get_last_message()

        trackMessage = await get_last_message()
        print(trackMessage)

        downloadTrackTask = asyncio.create_task(downloadTrackFromMessage(trackMessage))
        trackFile = await downloadTrackTask
        await app.delete_messages("me", trackMessage.id)
        playSongFromFile(trackFile)


async def appMain():
    while True:
        await playRandomTrack()


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


@app.on_message(filters.me)
async def my_handler(client, message):
    await downloadTrackFromMessage(message)


async def main228():
    async with app:
        await app.run()

start = time.time()
app.run(appMain())
# asyncio.run(main228())


# contact_phone = '+79538571643'
#
# contacts = await app.get_contacts()
# print(contacts)
#
# for contact in contacts:
#     if contact.phone_number == contact_phone:
#         await app.send_message(contact.username, 'text')
