def create_txts(output_dict: dict, date: str):
    for key, value in output_dict.items():
        with open(f'txts/output{date}_{key}.txt', 'w') as file:
            file.write("\n")
            for subject, name_0 in value[0].items():
                formatted_name_0 = " ".join(name_0.split())
                name_1 = value[1].get(subject, "")  # Получаем соответствующее имя из value[1]
                formatted_name_1 = " ".join(name_1.split()) if name_1 else ""  # Форматируем, если имя есть
                file.write(f"{subject} -> {formatted_name_0} -> {formatted_name_1}\n\n")