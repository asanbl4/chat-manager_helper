import asyncio
import os
import re

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

import reader_bot
import sender_bot
from main import main_func

load_dotenv()

TOKEN = os.getenv('MAIN_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()
SENDER_CHAT_ID = int(os.getenv("SENDER_CHAT_ID"))


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("""/date дата - выставляет сегодняшнюю дату для collect_data. дата в формате 17.08. выставления сегодняшней даты
    
/collect_data - собирает информацию по ТГ ОК/СП + собирает изображения расписаний

/send_schedule - высылает самое новое расписание в ЛС

/send_schedule_group - высылает расписание в группу Расписание ОК/СП

/send_shift - высылает список тех, кто не вышел на смену/резерв

/clean - чистит все записанные в программу сообщения. ПОСЛЕ ВСЕХ ОТМЕТОК ОЧИЩАТЬ.
    """)


@dp.message(Command('clean'))
async def clean_logs(message: Message):
    reader_bot.result.clear()
    open('to_send.txt', 'w').close()
    open('messages.txt', 'w').close()
    await message.answer('logs cleaned!')


@dp.message(Command('collect_data'))
async def run_main(message: Message):
    main_func()
    await message.answer('Данные собраны и готовы на отправку!')


@dp.message(Command('send_schedule'))
async def send_schedule(message: Message):
    await sender_bot.main(CHAT_ID=message.chat.id)
    await message.answer('sender bot started, check @chat_manager_helper_bot')


@dp.message(Command('send_schedule_group'))
async def send_schedule_group(message: Message):
    del message
    await sender_bot.main(SENDER_CHAT_ID)


@dp.message(Command('date'))
async def set_date(message: Message):
    pattern = re.compile(r'\d{2}.\d{2}')
    match = pattern.match(message.text.split()[1])
    if match:
        with open('dates.txt', 'w', encoding="UTF-8") as file:
            file.write(message.text.split()[1])
        await message.answer(f"Поставлена дата {message.text.split()[1]}")
    else:
        await message.answer(f"Формат даты некорректный!")


@dp.message(Command('send_shift'))
async def send_shift(message: Message):
    with open('to_send.txt', 'r') as file:
        file_contents = file.read()
        if file_contents:
            await bot.send_message(chat_id=message.chat.id, text=file_contents)
        else:
            await bot.send_message(chat_id=message.chat.id, text='Logs have been cleared recently')


async def main():
    print('main bot started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
