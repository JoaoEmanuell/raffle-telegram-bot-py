from PIL import Image
from pathlib import Path
from uuid import uuid4
from os.path import exists
from os import mkdir

BASE_DIR = Path(__file__).resolve()
main_dir = BASE_DIR.parent.parent.parent.parent
tmp_save_path = main_dir
base_raffles_image_path = f"{main_dir}/database/base_raffles_image"


def personalized_model_image(
    base_image: str,  # filename
    raffle_image_path: str,  # full path
    x: int,
    y: int,
    height: int,
    width: int,
) -> str:
    with Image.open(f"{base_raffles_image_path}/{base_image}") as new_image:
        with Image.open(raffle_image_path) as raffle_image:
            rectangle_coordinates = (int(x), int(y), int(height), int(width))
            raffle_image = raffle_image.resize((int(width), int(height)))
            new_image.paste(
                raffle_image, (rectangle_coordinates[0], rectangle_coordinates[1])
            )

    if not exists(f"{tmp_save_path}/tmp/"):
        mkdir(f"{tmp_save_path}/tmp/")

    image_name = f"{tmp_save_path}/tmp/{str(uuid4())}.png"

    new_image.save(image_name)

    return image_name
