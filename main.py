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
        dateStr = tracksFile.readline().strip()
        if len(dateStr) <= 0:
            break
        trackRow = (groupName, songName, dateStr)
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


def playSongFromFile(filename, startPlaying: float = 0.0):
    mixer.music.load(filename)
    mixer.music.play(start=startPlaying, fade_ms=1000)
    print(f"start second: {startPlaying}")
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)


async def playRandomTrack(fromBeginning: bool):
    async with app:
        global _startMeasure
        print(time.time() - _startMeasure)

        while True:
            row = trackDB[random.randrange(len(trackDB))]
            tracksStr = row[0] + " " + row[1]
            # print(tracksStr)

            _startMeasure = time.time()
            bot_results = await app.get_inline_bot_results(
                "murglar_bot",
                query=tracksStr
            )

            if bot_results.results[0].content.attributes[0].duration >= 25:
                break

        await app.send_inline_bot_result(
            "me", bot_results.query_id,
            bot_results.results[0].id)
        print(time.time() - _startMeasure)

        # wait when track was loaded to telegram's server

        _startMeasure = time.time()
        trackMessage = await get_last_message()
        # print(trackMessage)
        while trackMessage.reply_markup is not None:
            await asyncio.sleep(1)
            trackMessage = await get_last_message()
        trackMessage = await get_last_message()
        print(time.time() - _startMeasure)
        # print(trackMessage.audio)

        downloadTrackTask = asyncio.create_task(downloadTrackFromMessage(trackMessage))
        trackFile = await downloadTrackTask
        await app.delete_messages("me", trackMessage.id)

        # playSongFromFile("radioInit.mp3", 6)
        # playSongFromFile(
        #     io.BytesIO(trackFile.getbuffer()),
        #     0 if fromBeginning else random.randrange(0, trackMessage.audio.duration - 20))

        radioInitSound.play(maxtime=6000)
        await asyncio.sleep(5)
        mixer.music.load(io.BytesIO(trackFile.getbuffer()))
        # mixer.mu
        mixer.music.play(start=0)
        while mixer.music.get_busy():  # wait for music to finish playing
            await asyncio.sleep(1)
        # mixer.music.load(io.BytesIO(trackFile.getbuffer()))
        # mixer.music.play(start=0)
        # while mixer.music.get_busy():  # wait for music to finish playing
        #     await asyncio.sleep(1)

        _startMeasure = time.time()


async def appMain():
    await playRandomTrack(False)
    while True:
        await playRandomTrack(True)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


mixer.init()
radioInitSound = mixer.Sound("radioInit.ogg")

_startMeasure = time.time()
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
