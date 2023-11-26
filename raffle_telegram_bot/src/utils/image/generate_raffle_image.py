from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from uuid import uuid4
from os.path import exists
from os import mkdir

BASE_DIR = Path(__file__).resolve()
save_path = BASE_DIR.parent.parent.parent.parent


def generate_raffle_image(quantity: int = 100, marked_numbers: list[int] = []) -> str:
    # Calculate the number of lines required
    numbers_per_row = 10
    num_rows = quantity // numbers_per_row
    if quantity % numbers_per_row != 0:
        num_rows += 1

    # Create a new white image
    image_size = (
        numbers_per_row * 50,
        num_rows * 50,
    )
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    # Fonte and size
    font_size = 25
    font_dir = f"{BASE_DIR.cwd()}/assets/fonts"
    print(font_dir, save_path)
    font = ImageFont.truetype(f"{font_dir}/Arial.ttf", font_size)

    number = 1
    for i in range(num_rows):
        for j in range(numbers_per_row):
            if number > quantity:
                break
            x = j * 50
            y = i * 50
            draw.rectangle([x, y, x + 50, y + 50], outline="black")
            if str(number) in marked_numbers:
                # Red ball in the marked number
                draw.ellipse([x + 5, y + 5, x + 45, y + 45], fill="red")
            draw.text(
                (x + 25, y + 25), str(number), fill="black", font=font, anchor="mm"
            )
            number += 1

    if not exists(f"{save_path}/tmp/"):
        mkdir(f"{save_path}/tmp/")

    image_name = f"{save_path}/tmp/{str(uuid4())}.png"

    image.save(image_name)

    return image_name
