import asyncio
import os
import re
from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv

from csv_manager import manage_tg_csv

load_dotenv()

TOKEN = os.getenv('READER_BOT_TOKEN')
CHAT_ID = int(os.getenv('READER_CHAT_ID'))
RES_CHAT_ID = int(os.getenv('RES_CHAT_ID'))

bot = Bot(token=TOKEN)
dp = Dispatcher()

result = []


@dp.message()
async def log_message(message: Message):
    global result
    if message.chat.id == CHAT_ID:
        username = message.from_user.username or message.from_user.full_name
        text = message.text
        timestamp = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%H:%M')
        today = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%d.%m')
        # today = '23.08'
        hours, minutes = timestamp.split(":")
        # hours, minutes = ['11', '50']
        pattern = re.compile(r'(на смене|резерв(е)?)\s*\d{2}-\d{2}', re.IGNORECASE)
        try:
            match = pattern.search(text.lower())
        except Exception:
            match = pattern.search(text)
        # validation for на смене 12-14, резерв 12-14, в резерве 12-14
        if match:
            # validation for 11:48-11:57, 13:48-13:57
            if 48 <= int(minutes) <= 57 and int(hours) in [i for i in range(11, 23) if i % 2]:
                # check if there are already logged messages
                if not result:
                    data_list = await read_output_txt(f'txts/output{today}_{str(int(hours) + 1)}:00.txt')
                else:
                    data_list = result
                telegrams = manage_tg_csv.clean_data()

                with open('messages.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{username} : {text} - {timestamp}\n")
                    print(f"Logged message from {username}: {text}")

                with open('messages.txt', 'r', encoding='utf-8') as file:
                    lines = [line.rstrip('\n') for line in file.readlines()]
                    for line in lines:
                        logged_username = line.split()[0]
                        for tg, (name, subject) in telegrams.items():
                            if logged_username.lower() in tg.lower():
                                for data in data_list:
                                    osnova = data[1].split()
                                    rezerv = data[2].split()
                                    if name.split() == osnova:
                                        data[1] = ''
                                    elif name.split() == rezerv:
                                        data[2] = ''

                    result = data_list
                with open('to_send.txt', 'w') as file:
                    file.write('НЕ ВЫШЛИ😡\n\n')
                    for res in result:
                        file.write(f"{res[0]} | {f'**{res[1]}**' if res[1] else 'Y'} | {f'**{res[2]}**' if res[2] else 'Y'}\n\n")


async def read_output_txt(file_path):
    """
    reads output{date}_{time}.txt and returns list of tuples [()]
    - file_path parameter of the filepath i.e. txts/output19.08_20:00.txt
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data_list = []

    # Define a regular expression to match each line with subject, основа, and резерв
    pattern = re.compile(r'^(.{20})(.{25})(.{25})')

    for line in lines[4:]:
        match = pattern.match(line)
        if match:
            subject = match.group(1).strip()
            osnova = match.group(2).strip()
            rezerv = match.group(3).strip()
            if '-' not in subject:
                data_list.append([subject, osnova, rezerv])

    return data_list


async def main():
    print("reader bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

