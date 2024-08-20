import pandas as pd


def clean_data():
    df = pd.read_csv('csvs/tg_records.csv')
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={"По какому предмету ты будешь куратором?": "subject", "ФИ для графика": "name", "ТГ": "tg"},
              inplace=True)

    output_dict = {}
    for tg in df['tg'].unique():
        output_dict[tg] = list(map(lambda x: tuple(x), df[df['tg'] == tg][['name', 'subject']].values))[0]
    """
        {
            "Английский язык": ("Батырхан Асанали", "@asanbl4"),
        }
    """
    return output_dict
