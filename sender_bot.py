import os
import pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, InputMediaDocument, Message
import asyncio
from dotenv import load_dotenv
from main import main_func

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def send_files_from_folder(formatted_date):
    folder_path = 'imgs'
    media = []
    filenames = os.listdir(folder_path)
    for filename in sorted(filenames):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and formatted_date in file_path:
            file = FSInputFile(file_path)
            media.append(InputMediaDocument(media=file))
            print(
                f"Файл добавлен: {datetime.now(pytz.timezone('Asia/Almaty')).strftime('%Y-%m-%d %H:%M:%S')} - {filename}")

    if media:
        await bot.send_media_group(chat_id=CHAT_ID, media=media)
        await bot.send_message(chat_id=CHAT_ID, text=f"Расписание на день {formatted_date}.")
    else:
        print("Нет файлов для отправки.")


def prepare_data(formatted_date):
    with open('dates.txt', 'w', encoding="UTF-8") as file:
        file.write(formatted_date)
    main_func()


@dp.message()
async def log_message(message: Message):
    if message.chat.id == CHAT_ID:
        username = message.from_user.username or message.from_user.full_name
        text = message.text
        timestamp = datetime.now(pytz.timezone('Asia/Almaty')).strftime('%Y-%m-%d %H:%M:%S')

        with open('messages.txt', 'a', encoding='utf-8') as file:
            file.write(f"{username}: {text}\n - {timestamp}")

        print(f"Logged message from {username}: {text}")


async def main():
    print("bot started")
    with open('dates.txt') as file:
        formatted_date = file.readlines()[0].rstrip('\n')
    prepare_data(formatted_date)
    await send_files_from_folder(formatted_date)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
