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
close_result = []


def clean_result():
    global result, close_result
    result.clear()
    close_result.clear()


@dp.message()
async def log_message(message: Message):
    global result, close_result
    if message.chat.id == CHAT_ID:
        username = message.from_user.username or message.from_user.full_name
        text = message.text
        timestamp = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%H:%M')
        today = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%d.%m')
        # today = '23.08'
        hours, minutes = timestamp.split(":")
        # hours, minutes = ['20', '00']
        pattern_start = re.compile(r'(на смене|резерв(е)?)\s*\d{2}-\d{2}', re.IGNORECASE)
        match_start = pattern_start.search(text)
        pattern_stop = re.compile(r'завершил(а)?', re.IGNORECASE)
        match_stop = pattern_stop.search(text)

        telegrams = manage_tg_csv.clean_data()

        # validation for на смене 12-14, резерв 12-14, в резерве 12-14
        if match_start:
            # validation for 11:48-11:57, 13:48-13:57
            if 48 <= int(minutes) <= 57 and int(hours) in [i for i in range(11, 23) if i % 2]:
                # check if there are already logged messages
                if not result:
                    data_list = await read_output_txt(f'txts/output{today}_{str(int(hours) + 1)}:00.txt')
                else:
                    data_list = result

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
                    file.write('415 база ответьте😡🤬\n\n')
                    for res in result:
                        file.write(f"{res[0]} | {f'**{res[1]}**' if res[1] else 'Y'} | {f'**{res[2]}**' if res[2] else 'Y'}\n\n")
        if match_stop:
            # validation for 14:00-14:10
            if 0 <= int(minutes) <= 10 and int(hours) in [i for i in range(14, 23) if not i % 2]:
                if int(hours) != 22:
                    data_list_before = await read_output_txt(f'txts/output{today}_{str(int(hours) - 2)}:00.txt')
                    data_list_now = await read_output_txt(f'txts/output{today}_{str(int(hours))}:00.txt')
                    osnova_before = [data[1] for data in data_list_before]
                    osnova_now = [data[1] for data in data_list_now]
                    # validation if a person continues their shift
                    if not close_result:
                        for i in range(len(osnova_before)):
                            if osnova_now[i] == osnova_before[i]:
                                close_result.append('')
                            else:
                                close_result.append(' '.join(osnova_before[i].split()))
                else:
                    data_list_before = await read_output_txt(f'txts/output{today}_{str(int(hours) - 2)}:00.txt')
                    osnova_before = [data[1] for data in data_list_before]
                    if not close_result:
                        close_result = osnova_before

                with open('messages_close.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{username} : {text} - {timestamp}\n")
                    print(f"Logged closing message from {username}")

                osnova = ''
                subjects = [data[0] for data in data_list_before]

                with open('messages_close.txt', 'r', encoding='utf-8') as file:
                    lines = [line.rstrip('\n') for line in file.readlines()]
                    for line in lines:
                        logged_username = line.split()[0]
                        for tg, (name, subject) in telegrams.items():
                            if logged_username.lower() in tg.lower():
                                osnova = name.split()
                                break

                for i in range(len(osnova_before)):
                    el_before = osnova_before[i].split()
                    if osnova == el_before:
                        close_result[close_result.index(' '.join(el_before))] = ''

                with open('to_send_close.txt', 'w', encoding='utf-8') as file:
                    file.write(f"КТО ЗАБЫЛ ЗАКРЫТЬ?!?!?!?!\n\n")
                    for i, res in enumerate(close_result):
                        file.write(f"{subjects[i]} | {f'**{res}**' if res else 'Y'}\n\n")


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

