from csv_manager import manage_week_csv, manage_tg_csv, manage_manager_csv
from parser import week_parser, tg_parser, manager_parser
from txt_builder.txt_builder import create_txts


def main_func():
    try:
        # fetch and collect tg data of workers
        tg_parser.parser()
        # fetch and collect all shift data of managers
        manager_parser.parser()

        # prepare data for sending messages
        with open("./dates.txt") as file:
            filedates = [line.rstrip('\n') for line in file.readlines()]

        for filedate in filedates:
            # create csv files for sending bot
            week_parser.parser(filedate)
            # manage and clean csv file
            output_dict = manage_week_csv.clean_data(filedate)
            # managers list
            managers_list = manage_manager_csv.clean_csv(filedate)
            # create txt files
            create_txts(output_dict, filedate, managers_list)
    except Exception as e:
        print(e)
        return e


if __name__ == '__main__':
    main_func()
