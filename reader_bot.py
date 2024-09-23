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


def clean_result():
    with open('txts/result.txt', 'w') as f:
        f.close()


@dp.message()
async def log_message(message: Message):
    if message.chat.id == CHAT_ID:
        username = message.from_user.username or message.from_user.full_name
        text = message.text
        timestamp = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%H:%M')
        today = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%d.%m')
        # today = '23.08'
        hours, minutes = timestamp.split(":")
        pattern_start = re.compile(r'(на смене|резерв(е)?)\s*\d{2}-\d{2}', re.IGNORECASE)
        pattern_stop = re.compile(r'завершил(а)?', re.IGNORECASE)
        if text:
            text = text.replace('\n', ' ').lower()
            match_start = pattern_start.search(text)
            match_stop = pattern_stop.search(text)
            subject = text[text.find('#'):]
        else:
            match_start = False
            match_stop = False
            subject = ''

        telegrams = manage_tg_csv.clean_data()

        # validation for на смене 12-14, резерв 12-14, в резерве 12-14
        if match_start:
            # validation for 11:48-11:57, 13:48-13:57
            if 48 <= int(minutes) <= 57 and int(hours) in [i for i in range(11, 23) if i % 2]:
                # check if there are already logged messages
                data_list = []
                with open('txts/result.txt', encoding='utf-8') as file:
                    for line in file.readlines():
                        line = line.strip('\n').split('ng')
                        data_list.append((line[0], line[1], line[2]))

                if not data_list:
                    data_list = await read_output_txt(f'txts/output{today}_{str(int(hours) + 1)}:00.txt')
                data_list = [list(x) for x in data_list]
                for data in data_list:
                    subj = data[0].replace(' ', '').lower()
                    if subj in subject:
                        if 'смен' in text:
                            data[1] = ''
                        elif 'резер' in text:
                            data[2] = ''

                with open('txts/result.txt', 'w', encoding='utf-8') as file:
                    for data in data_list:
                        file.write(f'{data[0]}ng{data[1]}ng{data[2]}\n')

                with open('to_send.txt', 'w') as file:
                    file.write('415 база ответьте😡🤬\n\n')
                    for data in data_list:
                        file.write(f"{data[0]} | {f'**{data[1]}**' if data[1] else 'Y'} | {f'**{data[2]}**' if data[2] else 'Y'}\n\n")

        if match_stop:
            # validation for 14:00 - 14:10
            if 0 <= int(minutes) >= 10 and int(hours) in [hour for hour in range(14, 24, 2)]:
                data_list = []
                with open('txts/result_close.txt', encoding='utf-8') as file:
                    for line in file.readlines():
                        line = line.strip('\n').split('ng')
                        data_list.append((line[0], line[1], line[2]))

                if not data_list:
                    data_list = await read_output_txt(f'txts/output{today}_{str(int(hours))}:00.txt')
                data_list = [list(x) for x in data_list]
                try:
                    data_list2 = await read_output_txt(f'txts/output{today}_{str(int(hours) + 2)}:00.txt')
                    for i in range(len(data_list)):
                        osnova1 = data_list[i][1]
                        osnova2 = data_list2[i][1]
                        if osnova1 == osnova2:
                            data_list[i][1] = 'Y'
                except FileNotFoundError:
                    pass
                with open('txts/result_close.txt', 'w', encoding='UTF-8'):
                    for data in data_list:
                        file.write(f'{data[0]}ng{data[1]}ng{data[2]}\n')

                with open('to_send_close.txt', 'w') as file:
                    file.write('Кто не закрыл?😡🤬\n\n')
                    for data in data_list:
                        file.write(f"{data[0]} | {f'**{data[1]}**' if data[1] else 'Y'} | {f'**{data[2]}**' if data[2] else 'Y'}\n\n")


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

