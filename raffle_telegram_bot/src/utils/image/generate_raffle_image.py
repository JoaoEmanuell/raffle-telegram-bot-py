from PIL import Image, ImageDraw, ImageFont
from uuid import uuid4
from ..paths import base_path, tmp_path


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
    font_dir = f"{base_path}/assets/fonts"
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

    # add a border in the image
    border_size = 5
    bordered_image = Image.new(
        "RGB",
        (image_size[0] + 2 * border_size, image_size[1] + 2 * border_size),
        "black",
    )
    bordered_image.paste(image, (border_size, border_size))

    image_name = f"{tmp_path}/{str(uuid4())}.png"

    bordered_image.save(image_name)

    return image_name
