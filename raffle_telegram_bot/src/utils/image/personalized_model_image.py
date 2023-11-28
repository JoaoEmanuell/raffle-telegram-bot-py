from PIL import Image
from pathlib import Path
from uuid import uuid4
from os.path import exists
from os import mkdir

BASE_DIR = Path(__file__).resolve()
save_path = BASE_DIR.parent.parent.parent.parent


def personalized_model_image(
    base_image_path: str,
    raffle_image_path: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> str:
    with Image.open(base_image_path) as base_image:
        with Image.open(raffle_image_path) as raffle_image:
            rectangle_coordinates = (x1, y1, x2, y2)
            raffle_image = raffle_image.resize(
                (
                    rectangle_coordinates[2] - rectangle_coordinates[0],
                    rectangle_coordinates[3] - rectangle_coordinates[1],
                )
            )
            base_image.paste(raffle_image, rectangle_coordinates)

    if not exists(f"{save_path}/tmp/"):
        mkdir(f"{save_path}/tmp/")

        image_name = f"{save_path}/tmp/{str(uuid4())}.png"

        base_image.save(image_name)

        return image_name
