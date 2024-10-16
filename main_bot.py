import asyncio
import os
from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv

import reader_bot
import sender_bot
from main import main_func
from csv_manager import manage_tg_csv

load_dotenv()

TOKEN = os.getenv("MAIN_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
SENDER_CHAT_ID = int(os.getenv("SENDER_CHAT_ID"))

commands = [
    BotCommand(
        command="/date", description="Выставляет сегодняшнюю дату для collect_data"
    ),
    BotCommand(
        command="/collect_data",
        description="Собирает информацию по ТГ ОК/СП + изображения расписаний",
    ),
    BotCommand(
        command="/send_schedule", description="Высылает самое новое расписание в ЛС"
    ),
    BotCommand(
        command="/tg", description="Высылает Имя | ТГ сотрудников"
    ),
    BotCommand(
        command="/send_schedule_group",
        description="Высылает расписание в группу Расписание ОК/СП",
    ),
    BotCommand(
        command="/send_shift",
        description="Высылает список тех, кто не вышел на смену/резерв",
    ),
    # BotCommand(command='/send_close', description="Высылает список тех, кто не закрыл смену"),
    BotCommand(
        command="/clean", description="Чистит все записанные в программу сообщения"
    ),
]


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        """/date - выставляет сегодняшнюю дату для collect_data
    
/collect_data - собирает информацию по ТГ ОК/СП + собирает изображения расписаний

/send_schedule - высылает самое новое расписание в ЛС

/tg - высылает имя — тг сотрудников СП

/send_schedule_group - высылает расписание в группу Расписание ОК/СП

/send_shift - высылает список тех, кто не вышел на смену/резерв

/send_close - высылает список тех, кто не закрыл смену

/clean - чистит все записанные в программу сообщения. ПОСЛЕ ВСЕХ ОТМЕТОК ОЧИЩАТЬ.
    """
    )


@dp.message(Command("clean"))
async def clean_logs(message: Message):
    reader_bot.clean_result()
    open("to_send.txt", "w").close()
    open("messages.txt", "w").close()
    open("messages_close.txt", "w").close()
    open("to_send_close.txt", "w").close()
    await message.answer("logs cleaned!")


@dp.message(Command("collect_data"))
async def run_main(message: Message):
    resp = main_func()
    if not resp:
        await message.answer("Данные собраны и готовы на отправку!")
    else:
        await message.answer(f"Ошибка:\n\n{resp}")


@dp.message(Command("send_schedule"))
async def send_schedule(message: Message):
    await sender_bot.main(CHAT_ID=message.chat.id)
    await message.answer("sender bot started, check @chat_manager_helper_bot")


@dp.message(Command("tg"))
async def send_tg(message: Message):
    await write_tg_csv_to_txt()
    await send_file_from_path("tg.txt", message)


@dp.message(Command("send_schedule_group"))
async def send_schedule_group(message: Message):
    del message
    await sender_bot.main(SENDER_CHAT_ID)


@dp.message(Command("date"))
async def set_date(message: Message):
    with open("dates.txt", "w", encoding="UTF-8") as file:
        today = datetime.now(pytz.timezone("Asia/Almaty")).strftime("%d.%m")
        file.write(today)
    await message.answer(f"Поставлена дата {today}")


@dp.message(Command("send_shift"))
async def send_shift(message: Message):
    await send_file_from_path("to_send.txt", message)
    await send_tg_for_shift("to_send.txt", message)


@dp.message(Command("send_close"))
async def send_close(message: Message):
    await send_file_from_path("to_send_close.txt", message)


async def send_file_from_path(path, message):
    with open(path, "r") as file:
        file_contents = file.read()
        if file_contents:
            await bot.send_message(chat_id=message.chat.id, text=file_contents)
        else:
            await bot.send_message(
                chat_id=message.chat.id, text="Logs have been cleared recently"
            )


async def write_tg_csv_to_txt():
    clean_tgs = await clean_tg()
    with open("tg.txt", "w") as file:
        for full_name, tg_handle in sorted(clean_tgs):
            file.write(f"{full_name} | {tg_handle}\n")


async def clean_tg():
    telegrams = manage_tg_csv.clean_data()
    clean_tgs = []
    for tg_handle, (full_name, subject) in telegrams.items():
        if tg_handle[0] != "@":
            tg_handle = "@" + tg_handle
        surname, firstname = full_name.split()
        clean_tgs.append((surname + " " + firstname, tg_handle))
    return clean_tgs


async def send_tg_for_shift(filepath, message):
    clean_tgs = await clean_tg()
    osnovas = []
    rezervs = []
    with open(filepath) as file:
        lines = file.readlines()
        for line in lines[1:]:
            line = line.rstrip('\n')
            if line:
                subject, osnova, rezerv = line.split(" | ")
                osnovas.append(osnova)
                rezervs.append(rezerv)
    clean_tgs_dict = dict(clean_tgs)
    msg_to_resend = 'Основа\n'
    msg_txt = 'Основа\n'
    for osnova in osnovas:
        osnova = osnova.strip("**")
        if not osnova == "Y":
            msg_txt += f"{osnova} {clean_tgs_dict.get(osnova)}\n"
            msg_to_resend += f"{clean_tgs_dict.get(osnova)}\n"
    msg_to_resend += 'Резерв\n'
    msg_txt += 'Резерв\n'
    for rezerv in rezervs:
        rezerv = rezerv.strip("**")
        if not rezerv == "Y":
            msg_txt += f"{rezerv} {clean_tgs_dict.get(rezerv)}\n"
            msg_to_resend += f"{clean_tgs_dict.get(rezerv)}\n"
    await bot.send_message(chat_id=message.chat.id, text=msg_txt)
    await bot.send_message(chat_id=message.chat.id, text=msg_to_resend)


async def main():
    print("main bot started")
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
