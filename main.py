import asyncio
import io
import math
import os.path
import random
import logging
import datetime
import time
import json
import sys
from pathlib import Path

from pyrogram import Client

from mutagen.mp3 import MP3
from pygame import mixer  # Load the popular external library


async def progress(current, total):
    if total <= 0:
        mainLogger.info(f'Процент загрузки трека: empty')
    else:
        mainLogger.info(f'Процент загрузки трека: {current * 100 / total:.0f}%')


class RadioChaos:
    def __init__(self):
        mixer.init()
        self.radioInitSound = mixer.Sound("sounds/radioInit.ogg")
        pass

    async def get_last_message(self):
        async for message in app.get_chat_history("me", limit=1, offset_id=-1):
            return message

    async def downloadTrackFromMessage(self, message):
        print("start downloading")
        file = await app.download_media(message, progress=progress, in_memory=True)
        print("finish downloading")
        return file

    def playSongFromFile(self, filename, startPlaying: float = 0.0):
        mixer.music.load(filename)
        mixer.music.play(start=startPlaying, fade_ms=1000)
        print(f"start second: {startPlaying}")
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)

    async def playRandomTrack(self, isRadioStarts: bool):
        async with app:
            global _startMeasure
            mainLogger.info(f'Время перехода между итерациями: {time.time() - _startMeasure:.1f}s')

            self.radioInitSound.play(loops=-1)

            debugLastSong = True
            while True:
                if not debugLastSong:
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

                    mainLogger.info(f'Время поиска трека: {time.time() - _startMeasure:.1f}s')

                # wait when track was loaded to telegram's server

                _startMeasure = time.time()
                trackMessage = await self.get_last_message()
                while trackMessage.reply_markup is not None:
                    await asyncio.sleep(1)
                    trackMessage = await self.get_last_message()
                trackMessage = await self.get_last_message()
                mainLogger.info(f'Время ожидания загрузки трека на сервер телеграма: '
                                f'{time.time() - _startMeasure:.0f}s')
                if debugLastSong:
                    break

                if not debugLastSong:
                    if trackMessage.audio.duration >= 25:
                        break
                    else:
                        # Трек не загрузился, но сообщение осталось с сообщением
                        # о незакаченном треке, поэтому его нужно удалить
                        await app.delete_messages("me", trackMessage.id)

            # todo: uncomment when release
            self.radioInitSound.stop()

            partTrack = bytes()
            sizeOfChunks = 0
            isStartPlaying = False
            trackSize = trackMessage.audio.file_size
            try:
                i = 1
                async for chunk in app.stream_media(trackMessage):
                    partTrack += chunk
                    sizeOfChunks += len(chunk)
                    mainLogger.info(f'Loaded {i}\'s part')
                    i += 1
                    if not isStartPlaying and sizeOfChunks > 2000e3:      # 2Mb
                        mainLogger.info('First part loaded to play')
                        song = MP3(io.BytesIO(partTrack))
                        songLength = song.info.length
                        print(f'sizeOfChunks {sizeOfChunks:10f}')
                        print(f'trackSize    {trackSize:10f}')
                        songMinutes, songSeconds = divmod(songLength, 60)
                        print(f'songLength   {songMinutes:.0f}m {songSeconds:.0f}s')

                        # INFO: firstSongPartLength - не совсем настоящая длина части трека. MP3 файл это в первую
                        # очередь сжатый файл. Сжатые части трека зависят друг от друга. Чтобы декодировать одну часть,
                        # нужна предыдущая часть или бывает даже следующая. Поэтому мы не всегда можем проиграть
                        # всю часть трека целиком и полностью. Попробуем вначале отсечь 45% трека - магическое число
                        firstSongPartLength = songLength * sizeOfChunks / trackSize * 0.55
                        mainLogger.info(f'First part of song length: {firstSongPartLength:.0f}s')
                        mixer.music.load(io.BytesIO(partTrack))
                        mixer.music.play()
                        _startMeasure = time.time()
                        isStartPlaying = True

                # baseVolume = radioInitSound.get_volume()
                songVolume = mixer.music.get_volume()
                timeout = 1
                while mixer.music.get_busy():  # wait for music to finish playing
                    await asyncio.sleep(timeout)
                    pos = mixer.music.get_pos() / 1000
                    print(pos)
                    if firstSongPartLength - pos < 4:
                        if not mixer.Channel(0).get_busy():
                            # radioInitSound.set_volume(0.1 * baseVolume)
                            mixer.Channel(0).play(self.radioInitSound, loops=-1)
                            baseVolume = mixer.Channel(0).get_volume()
                            mixer.Channel(0).set_volume(0.1 * baseVolume)
                            timeout = 0.1
                        else:
                            mixer.Channel(0).set_volume(mixer.Channel(0).get_volume() + 0.1 * baseVolume)
                            mixer.music.set_volume(mixer.music.get_volume() - songVolume * 0.1)
                    if firstSongPartLength - pos < 2:
                        break

                # pos =
                mixer.music.load(io.BytesIO(partTrack))
                mixer.music.play(start=mixer.music.get_pos()/1000)
                # print(pos)
                while mixer.music.get_busy():  # wait for music to finish playing
                    await asyncio.sleep(timeout)
                    vol = mixer.Channel(0).get_volume()
                    songVol = mixer.music.get_volume()
                    if songVol >= songVolume:
                        self.radioInitSound.stop()
                        timeout = 1
                    else:
                        mixer.Channel(0).set_volume(vol - baseVolume * 0.1)
                        mixer.music.set_volume(mixer.music.get_volume() + songVolume * 0.1)
            except Exception as ex:
                print(ex)

            # trackFile = await downloadTrackTask

            # mainLogger.info(f'Трек загрузился')
            # todo: uncomment when release
            # await app.delete_messages("me", trackMessage.id)

            songPositionPlaying = 0 if not isRadioStarts \
                else random.randrange(0, trackMessage.audio.duration - 20)

            # mixer.music.load(io.BytesIO(trackFile.getbuffer()))
            # mixer.music.play(start=songPositionPlaying)

            trackMinutes, trackSeconds = divmod(math.floor(time.time() - _startMeasure), 60)
            mainLogger.info(f'Трек играл: {trackMinutes}m {trackSeconds}s')

            _startMeasure = time.time()

    async def windUp(self):
        await self.playRandomTrack(isRadioStarts=True)
        while True:
            await self.playRandomTrack(isRadioStarts=False)


if __name__ == "__main__":
    logsDir = 'logs/'
    if not os.path.exists(logsDir):
        Path(logsDir).mkdir(exist_ok=True)
    logFileName = logsDir + 'main.log'
    Path(logFileName).touch(exist_ok=True)

    fileLogHandler = logging.FileHandler(filename=logFileName, encoding="utf-8", mode="a")
    fileLogHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    mainLogger = logging.getLogger(__name__)
    mainLogger.setLevel(logging.INFO)
    mainLogger.addHandler(logging.StreamHandler(sys.stdout))
    mainLogger.addHandler(fileLogHandler)

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

    global _startMeasure
    _startMeasure = time.time()
    shuffle = RadioChaos()
    app.run(shuffle.windUp())
