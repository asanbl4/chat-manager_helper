import pandas as pd


def clean_data(filedate: str) -> dict:
    df = pd.read_csv(f"csvs/parser_output_{filedate}.csv")
    df.fillna("", inplace=True)

    # Delete rows with НЕ занимать && delete row with days of the week
    df_cleaned = df[df["Служба поддержки"] != "НЕ занимать"].drop(1, axis=0)
    df_cleaned = df_cleaned.drop(0, axis=0)
    # rename first column normally
    df_cleaned.rename(columns={"Unnamed: 0": "Время"}, inplace=True)
    # stay only the time of the start
    df_cleaned["Время"] = df_cleaned["Время"].map(
        lambda x: x[5:-8] if "Чаты" in x else x
    )
    # reset index after deletion of some rows
    df_cleaned.reset_index(drop=True, inplace=True)

    output_dict = {}
    for i in range(0, 10, 2):
        row = df_cleaned.iloc[i]
        output_dict[row["Время"]] = [row[1:], df_cleaned.iloc[i + 1][1:]]

    return output_dict
