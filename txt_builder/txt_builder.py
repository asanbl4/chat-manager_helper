import os
from PIL import ImageFont, Image, ImageDraw


def create_images_from_textfile(file_path, image_path):
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        text = file.read()

    font_path = "dejavu-sans-mono/DejaVuSansMono.ttf"
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    padding = 20
    lines = text.splitlines()
    max_line_length = max([len(line) for line in lines])

    image_width = max_line_length * font_size // 2 + padding * 2 + 100
    image_height = (len(lines) + 1) * font_size + padding * 2 + 20

    if image_width > 2000:
        font_size = int(2000 / (max_line_length * font_size // 2) * font_size)
        font = ImageFont.truetype(font_path, font_size)
        image_width = max_line_length * font_size // 2 + padding * 2 + 100

    image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    for i, line in enumerate(lines):
        draw.text((padding, padding + i * font_size), line, font=font, fill=(0, 0, 0))

    image.save(image_path)
    print(f"Image saved: {image_path}")


def create_txts(output_dict: dict, date: str):
    for key, value in output_dict.items():
        filename = f'output{date}_{key}.txt'
        file_path = os.path.join('txts', filename)

        with open(file_path, 'w', encoding="utf-8-sig") as file:
            file.write(f"{key}-{str(int(key[:2]) + 2) + key[2:]}\n\n")
            file.write(f"{'Subject':<20}{'Основа':<25}{'Резерв':<25}\n")
            file.write("=" * 70 + "\n")
            for subject, name_0 in value[0].items():
                formatted_name_0 = " ".join(name_0.split())
                name_1 = value[1].get(subject, "")
                formatted_name_1 = " ".join(name_1.split()) if name_1 else ""
                file.write(f"{subject:<20}{formatted_name_0:<25}{formatted_name_1:<25}\n")
                file.write("-" * 70 + "\n")

        imgs_folder = 'imgs'
        os.makedirs(imgs_folder, exist_ok=True)
        image_path = os.path.join(imgs_folder, filename.replace('.txt', '.png'))
        create_images_from_textfile(file_path, image_path)
