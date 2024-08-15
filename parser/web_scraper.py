import csv
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv

load_dotenv()

# Oauth2 settings
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("parser/" + os.getenv('CRED_FILENAME'), scope)
client = gspread.authorize(creds)

spreadsheet_url = os.getenv("FILE_URL")
spreadsheet = client.open_by_url(spreadsheet_url)


def parser(filedate):
    sheet = spreadsheet.worksheet(filedate)

    # Чтение всех данных с листа
    data = sheet.get_all_records()

    # Путь к файлу для сохранения CSV
    csv_filename = f"csvs/parser_output_{filedate}.csv"

    # Сохранение данных в CSV файл
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Данные сохранены в файл {csv_filename}")
    return csv_filename
