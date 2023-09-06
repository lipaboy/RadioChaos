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


async def playRandomTrack(isRadioStarts: bool):
    async with app:
        global _startMeasure
        print(time.time() - _startMeasure)

        radioInitSound.play(loops=-1)

        _startMeasure = time.time()
        while True:
            row = trackDB[random.randrange(len(trackDB))]
            tracksStr = row[0] + " " + row[1]
            # print(tracksStr)

            bot_results = await app.get_inline_bot_results(
                "murglar_bot",
                query=tracksStr
            )

            if len(bot_results.results) <= 0 or \
                    not hasattr(bot_results.results[0], "content"):
                continue
            elif bot_results.results[0].content.attributes[0].duration >= 25:
                break

        await app.send_inline_bot_result(
            "me", bot_results.query_id,
            bot_results.results[0].id)
        print(time.time() - _startMeasure)

        # wait when track was loaded to telegram's server

        _startMeasure = time.time()
        trackMessage = await get_last_message()
        while trackMessage.reply_markup is not None:
            await asyncio.sleep(1)
            trackMessage = await get_last_message()
        trackMessage = await get_last_message()
        print(time.time() - _startMeasure)

        downloadTrackTask = asyncio.create_task(downloadTrackFromMessage(trackMessage))
        trackFile = await downloadTrackTask
        await app.delete_messages("me", trackMessage.id)

        songPositionPlaying = 0 if isRadioStarts \
            else random.randrange(0, trackMessage.audio.duration - 20)

        mixer.music.load(io.BytesIO(trackFile.getbuffer()))
        mixer.music.play(start=songPositionPlaying)

        await asyncio.sleep(1)
        radioInitSound.stop()
        while mixer.music.get_busy():  # wait for music to finish playing
            await asyncio.sleep(1)

        _startMeasure = time.time()


async def appMain():
    await playRandomTrack(isRadioStarts=True)
    while True:
        await playRandomTrack(isRadioStarts=False)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


mixer.init()
radioInitSound = mixer.Sound("radioInit.ogg")

_startMeasure = time.time()
app.run(appMain())