def create_txts(output_dict: dict, date: str):
    for key, value in output_dict.items():
        with open(f'txts/output{date}_{key}.txt', 'w', encoding="utf-8-sig") as file:
            file.write("\n")
            file.write(f"{'Subject':<20}{'Основа':<25}{'Резерв':<25}\n")
            file.write("="*70 + "\n")
            for subject, name_0 in value[0].items():
                formatted_name_0 = " ".join(name_0.split())
                name_1 = value[1].get(subject, "")
                formatted_name_1 = " ".join(name_1.split()) if name_1 else ""
                file.write(f"{subject:<20}{formatted_name_0:<25}{formatted_name_1:<25}\n")
                file.write("-"*70 + "\n")
