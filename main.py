from csv_manager.manage_csv import clean_data
from parser import web_scraper
from txt_builder.txt_builder import create_txts


def main():
    with open("./dates.txt") as file:
        filedates = [line.rstrip('\n') for line in file.readlines()]

    for filedate in filedates:
        # create csv files
        web_scraper.parser(filedate)
        # manage and clean csv file
        output_dict = clean_data(filedate)
        # create txt files
        create_txts(output_dict, filedate)


if __name__ == '__main__':
    main()
