import csv

from parser.week_parser import spreadsheet


def parser():
    sheet = spreadsheet.worksheet("МЧ")

    data = sheet.get_all_records()

    csv_filename = f"csvs/manager_records.csv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Данные сохранены в файл {csv_filename}")

    return csv_filename
