import pandas as pd


def clean_csv(filedate: str):
    df = pd.read_csv('csvs/manager_records.csv')
    df.rename(columns={"Unnamed: 0": "shifts"}, inplace=True)
    df["shifts"] = df["shifts"].map(lambda x: x.lstrip("Смена\n")[:2] if type(x) is not float else x)
    today = f"{filedate}"
    managers = {
        '12': df.loc[df['shifts'] == '12', today].unique()[0],
    }
    if df.loc[df['shifts'] == '12', today].unique()[0] != df.loc[df['shifts'] == '15', today].unique()[0]:
        managers[
            '14'] = f"""{df.loc[df['shifts'] == '12', today].unique()[0]}, {df.loc[df['shifts'] == '15', today].unique()[0]}"""
    else:
        managers['14'] = df.loc[df['shifts'] == '12', today].unique()[0]
    if df.loc[df['shifts'] == '15', today].unique()[0] != df.loc[df['shifts'] == '17', today].unique()[0]:
        managers[
            '16'] = f"""{df.loc[df['shifts'] == '15', today].unique()[0]}, {df.loc[df['shifts'] == '17', today].unique()[0]}"""
    else:
        managers['16'] = df.loc[df['shifts'] == '15', today].unique()[0]
    if df.loc[df['shifts'] == '17', today].unique()[0] != df.loc[df['shifts'] == '19', today].unique()[0]:
        managers[
            '18'] = f"""{df.loc[df['shifts'] == '17', today].unique()[0]}, {df.loc[df['shifts'] == '19', today].unique()[0]}"""
    else:
        managers['18'] = df.loc[df['shifts'] == '17', today].unique()[0]
    managers['20'] = df.loc[df['shifts'] == '19', today].unique()[0]
    return list(managers.values())

