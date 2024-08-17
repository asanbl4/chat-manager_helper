import os
import pytz
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaDocument
import asyncio
from dotenv import load_dotenv
from main import main_func
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def send_files_from_folder(bot, formatted_date):
    folder_path = 'imgs'
    media = []
    filenames = os.listdir(folder_path)
    for filename in sorted(filenames):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and formatted_date in file_path:
            file = FSInputFile(file_path)
            media.append(InputMediaDocument(media=file))
            print(f"Файл добавлен: {datetime.now(pytz.timezone('Asia/Almaty')).strftime('%Y-%m-%d %H:%M:%S')} - {filename}")

    if media:
        await bot.send_media_group(chat_id=CHAT_ID, media=media)
        await bot.send_message(chat_id=CHAT_ID, text=f"Расписание на день {formatted_date}.")
    else:
        print("Нет файлов для отправки.")


def prepare_data(formatted_date):
    with open('dates.txt', 'w', encoding="UTF-8") as file:
        file.write(formatted_date)
    main_func()


async def main():
    print("bot started")
    with open('dates.txt') as file:
        formatted_date = file.readlines()[0].rstrip('\n')
    async with Bot(token=TOKEN) as bot:
        await send_files_from_folder(bot, formatted_date)


if __name__ == '__main__':
    asyncio.run(main())


# async def schedule_job():
#     hours, minutes = 10, 0
#     almaty_tz = pytz.timezone('Asia/Almaty')
#     scheduler = await aiojobs.create_scheduler()
#
#     while True:
#         now = datetime.now(almaty_tz)
#         formatted_date = now.strftime("%d.%m")
#         current_time = now.strftime('%Y-%m-%d %H:%M:%S')
#         print(f"Текущее время в Алматы: {current_time}")
#
#         target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
#         if now > target_time:
#             target_time += timedelta(days=1)
#         delay = (target_time - now).total_seconds()
#         print(f"Следующее выполнение через: {int(delay)} seconds")
#
#         await asyncio.sleep(delay)
#         prepare_data(formatted_date)
#         await scheduler.spawn(send_files_from_folder(formatted_date))
#         await asyncio.sleep(360)
