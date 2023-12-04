from os import remove

from .generate_raffle_image import generate_raffle_image
from .personalized_model_image import personalized_model_image


async def handler_generate_image(raffle: dict) -> str:
    """Handler to manage a generation of raffles image, if raffle has a base image, then the application generate a raffle with a base image, else generate a simple image

    Args:
        raffle (dict): dict with raffle

    Returns:
        str: path to image
    """
    numbers = int(raffle["numbers"])
    marked_numbers = str(raffle["marked_numbers"]).split(" ")  # transform to a list
    image_base = raffle["image_base"]
    image_path = generate_raffle_image(numbers, marked_numbers)
    if image_base != "":
        image_base_rectangle_positions = raffle["image_base_rectangle_positions"].split(
            " "
        )  # transform to a list
        image_base_rectangle_positions_dict = {
            "x": image_base_rectangle_positions[0],
            "y": image_base_rectangle_positions[1],
            "height": image_base_rectangle_positions[2],
            "width": image_base_rectangle_positions[3],
        }
        personalized_image = personalized_model_image(
            image_base, image_path, **image_base_rectangle_positions_dict
        )
        remove(image_path)  # delete the simple image
        return personalized_image
    return image_path
