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
        # today = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%d.%m')
        today = '17.08'
        # hours, minutes = timestamp.split(":")
        hours, minutes = 11, 55
        pattern = re.compile(r'(на смене|резерв(е)?)\s*\d{2}-\d{2}', re.IGNORECASE)
        match = pattern.search(text.lower())
        # validation for на смене 12-14, резерв 12-14, в резерве 12-14
        if match:
            # validation for 11:54-11:59, 13:54-13:59
            if int(minutes) >= 54 and hours in [i for i in range(11, 23) if i % 2]:
                # check if there are already logged messages
                if not result:
                    # check in output txt files for the shift and make true
                    data_list = await read_output_txt(f'txts/output{today}_{str(int(hours) + 1)}:00.txt')
                else:
                    data_list = result
                telegrams = manage_tg_csv.clean_data()
                res_list = []
                for data in data_list:
                    for key, val in telegrams.items():
                        full_name, subject = val
                        tg = key
                        subj, osnova, rezerv = data
                        if username in tg:
                            if full_name == osnova:
                                res_list.append((subj, '', rezerv))
                            elif full_name == rezerv:
                                res_list.append((subj, osnova, ''))
                            else:
                                res_list.append(data)
                result = res_list
                text_for_send = ["НЕ ВЫШЛИ 😡"]
                for res in res_list:
                    subj, osnova, rezerv = res
                    if osnova or rezerv:
                        text_for_send.append(f"{subj.upper()}:\n{osnova} - основа\n{rezerv} - резерв")

                with open('messages.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{username}: {text} - {timestamp}\n")

                with open('messages.txt', 'r', encoding='utf-8') as file:
                    number_of_messages = len(file.readlines())

                if 15 <= number_of_messages <= 20:
                    await bot.send_message(RES_CHAT_ID, text='\n\n'.join(text_for_send))
                elif number_of_messages > 20:
                    # if too much results logged, truncate file
                    open('messages.txt', 'w').close()

                print(f"Logged message from {username}: {text}")


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
                data_list.append((subject, osnova, rezerv))

    return data_list


async def main():
    print("reader bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

