import os
import pytz
from datetime import datetime, timedelta
from telegram import Bot
import aiojobs
import asyncio
from dotenv import load_dotenv
from main import main_func
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)


async def send_files_from_folder(formatted_date):
    folder_path = 'txts'

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and formatted_date in file_path:
            with open(file_path, 'rb') as file:
                await bot.send_document(chat_id=CHAT_ID, document=file)
                print(f"Файл отправлен: {datetime.now(pytz.timezone('Asia/Almaty')).strftime('%Y-%m-%d %H:%M:%S')} - {filename}")
    await bot.send_message(chat_id=CHAT_ID, text="Расписание на день.\n"
                                                 "Подробнее смотреть по ссылке: "
                                                 "https://docs.google.com/spreadsheets/d/1ajRuaL7pAIIoi4XkIbhgQxE2lXll-x05cRA0znzkxeY/edit?gid=2139997612#gid=2139997612")


async def schedule_job():
    hours, minutes = 23, 37
    almaty_tz = pytz.timezone('Asia/Almaty')
    scheduler = await aiojobs.create_scheduler()

    while True:
        now = datetime.now(almaty_tz)
        formatted_date = now.strftime("%d.%m")
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Текущее время в Алматы: {current_time}")

        target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        print(f"Следующее выполнение через: {int(delay)} seconds")

        await asyncio.sleep(delay)
        prepare_data(formatted_date)
        await scheduler.spawn(send_files_from_folder(formatted_date))
        await asyncio.sleep(10)


def prepare_data(formatted_date):
    with open('dates.txt', 'w') as file:
        file.write(formatted_date)
    main_func()


if __name__ == '__main__':
    print("bot started")
    asyncio.run(send_files_from_folder("16.08"))
