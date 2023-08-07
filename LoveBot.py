from pyrogram import Client

import time
import json


with open("config.txt", encoding="utf-8") as configFile:
    config = json.load(configFile)

app = Client("my_account", api_id=config["api_id"], api_hash=config["api_hash"])

toWhom = "me"


"""
    Сука, есть три разные раскладки смайликов и пробелов в зависимости от устройства:
        1) Андроид, сообщение без фона (когда нет букв и других специальных символов. 
        Ток смайлики и пробелы)
        2) Андроид, сообщение с фоном (достаточно добавить пустой символ  )
        3) Десктоп, Windows 10 (только с фоном, без фона нет варианта)

"""

# msg = '❤️🧡💛💚💙💜💔❣️💕💞💓💗💖💘💝'
emptySymbol = ' '
messageList = []


def addMsg(message: str, dt: float):
    messageList.append((message, dt / 1000))


addMsg('Привет', 1500)
addMsg('Любимая', 1700)
addMsg('Ты готова?', 1000)
addMsg('5 secs.', 1000)
addMsg('4 secs..', 900)
addMsg('3 secs...', 900)
addMsg('2 secs.', 800)
addMsg('1 seca..', 800)
addMsg('0 sex...', 800)
addMsg('0 sex....', 700)
addMsg('0 sex.....', 700)
addMsg('0 sex......', 600)
addMsg('0 sex......!', 500)
addMsg('0 sex......!!', 500)
addMsg('0 sex......!!!', 500)
addMsg('0 sex......!!!!', 400)
addMsg('0 sex......!!!!!', 300)
addMsg('0 sex......!!!!!!!', 300)
addMsg('0 sex......!!!!!!!!!', 300)
addMsg('0 sex......!!!!!!!!!!!', 300)

form = """
💞                                          💞
 
   {}{}        {}{}  
 {}{}{}   {}{}{}
{}{}{}{}{}{}{}
     {}{}{}{}{}  
         {}{}{}    
              {}      
 
💞                                          💞
"""

formLines = form.splitlines()
form = '\n'.join([
    ('         ' if i in range(2, len(formLines) - 2) else '')
    + formLines[i] for i in range(0, len(formLines))
])

heartCount = form.count("{}")
heartsTuple = ('❤️',) * heartCount
msg = form.format(*heartsTuple)
addMsg(msg, 100)


def replaceElem(tp, pos: int, newElem: str):
    lst = list(tp)
    lst[pos] = newElem
    return tuple(lst)

"""
   {00}{01}      {02}{03}  
 {04}{05}{06}  {07}{08}{09}
{10}{11}{12}{13}{14}{15}{16}
     {17}{18}{19}{20}{21}  
        {22}{23}{24}    
            {25}                                          💞
"""

# heartsTuple = ('❤️',) * 13 + ('💛',) + ('❤️',) * (heartCount - 13 - 1)
positionOrder = [13, 6, 1, 0, 4, 10, 17, 22, 25, 24, 21, 16, 9, 3, 2, 7]
for pos in positionOrder:
    heartsTuple = replaceElem(heartsTuple, pos, '💛')
    msg = form.format(*heartsTuple)
    addMsg(msg, 250)

positionOrder = [(12, 14), (5, 8), (11, 15), (18, 20), (23, 23), (19, 19)]
for pos in positionOrder:
    heartsTuple = replaceElem(heartsTuple, pos[0], '💛')
    heartsTuple = replaceElem(heartsTuple, pos[1], '💛')
    msg = form.format(*heartsTuple)
    addMsg(msg, 250)


@app.on_message()
async def my_handler(client, message):
    if len(messageList) <= 0:
        pass

    time.sleep(messageList[0][1])
    newMsg = await app.send_message(toWhom, messageList[0][0])
    mainMsg = newMsg
    for i in range(1, len(messageList)):
        time.sleep(messageList[i][1])
        # editMsg(mainMsg.chat.id, messageList[i][0], mainMsg.id)
        currMsg = await app.edit_message_text(chat_id=mainMsg.chat.id,
                                              text=messageList[i][0],
                                              message_id=mainMsg.id)
        newMsg = currMsg
    time.sleep(1)
    await app.delete_messages(chat_id=mainMsg.chat.id,
                              message_ids=[newMsg.id])


app.run()
