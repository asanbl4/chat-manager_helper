import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

import sender_bot
from main import main_func

load_dotenv()

TOKEN = os.getenv('MAIN_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("""/collect_data - собирает информацию
/send_data - высылает самое новое расписание в чат
    """)


@dp.message(Command('collect_data'))
async def run_main(message: Message):
    main_func()
    await message.answer('Данные собраны и готовы на отправку!')


@dp.message(Command('send_data'))
async def send_data(message: Message):
    asyncio.run(sender_bot.main())
    await message.answer('sender bot started')


async def main():
    print('main bot started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
