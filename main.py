import parser.tg_parser
from csv_manager import manage_week_csv, manage_tg_csv
from parser import week_parser, tg_parser
from txt_builder.txt_builder import create_txts


def main_func():
    # fetch and collect tg data of workers
    tg_parser.parser()

    # prepare data for sending messages
    with open("./dates.txt") as file:
        filedates = [line.rstrip('\n') for line in file.readlines()]

    for filedate in filedates:
        # create csv files for sending bot
        week_parser.parser(filedate)
        # manage and clean csv file
        output_dict = manage_week_csv.clean_data(filedate)
        # create txt files
        create_txts(output_dict, filedate)


if __name__ == '__main__':
    main_func()
