import os
import pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, InputMediaDocument, Message
import asyncio
from dotenv import load_dotenv
from main import main_func

load_dotenv()

TOKEN = os.getenv("SENDER_BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def send_files_from_folder(formatted_date, CHAT_ID):
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
        await bot.send_message(chat_id=CHAT_ID, text=f"""No files to send: write /collect_data to the @umsch_main_helper_bot;
OR check this google document:
https://docs.google.com/spreadsheets/d/1ajRuaL7pAIIoi4XkIbhgQxE2lXll-x05cRA0znzkxeY/edit?gid=2139997612#gid=2139997612""")


def prepare_data(formatted_date):
    with open('dates.txt', 'w', encoding="UTF-8") as file:
        file.write(formatted_date)
    main_func()


async def main(CHAT_ID):
    print("bot started")
    with open('dates.txt') as file:
        formatted_date = file.readlines()[0].rstrip('\n')
    # prepare_data(formatted_date)
    await send_files_from_folder(formatted_date, CHAT_ID)
    # await dp.start_polling(bot)
    await bot.session.close()


if __name__ == '__main__':
    CHAT_ID = int(os.getenv("SENDER_CHAT_ID"))
    asyncio.run(main(CHAT_ID))
