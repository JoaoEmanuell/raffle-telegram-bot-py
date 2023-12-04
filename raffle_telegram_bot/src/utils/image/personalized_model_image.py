from PIL import Image
from uuid import uuid4

from ..paths import tmp_path, save_base_image_path


def personalized_model_image(
    base_image: str,  # filename
    raffle_image_path: str,  # full path
    x: int,
    y: int,
    height: int,
    width: int,
) -> str:
    with Image.open(f"{save_base_image_path}/{base_image}") as new_image:
        with Image.open(raffle_image_path) as raffle_image:
            rectangle_coordinates = (int(x), int(y), int(height), int(width))
            raffle_image = raffle_image.resize((int(width), int(height)))
            new_image.paste(
                raffle_image, (rectangle_coordinates[0], rectangle_coordinates[1])
            )

    image_name = f"{tmp_path}{str(uuid4())}.png"

    new_image.save(image_name)

    return image_name
