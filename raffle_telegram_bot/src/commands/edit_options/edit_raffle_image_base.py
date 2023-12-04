from os import getenv
from os.path import basename

from typing import Callable
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from dotenv import load_dotenv

from requests import post

load_dotenv()

EXTRACTOR_RED_RECTANGLE_API = getenv("EXTRACTOR_RED_RECTANGLE_API")


async def edit_raffle_image_base(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raffle: dict,
    image_base: str,
    update_raffle: Callable,
) -> None:
    raffle_name = raffle["name"]
    chat_id = context._chat_id
    user_id = context._user_id

    # extract the red rectangle positions

    with open(image_base, "rb") as file:
        await update.message.reply_text(
            "Iniciando processo de análise da imagem, aguarde um pouco!"
        )
        response = post(
            f"{EXTRACTOR_RED_RECTANGLE_API}/extract", files={"file": file}, timeout=60
        )
        json = response.json()

        # validate if found the red rectangle

        try:
            # error
            if json["msg"] == "Error to extract the rectangle":
                await update.message.reply_text(
                    "O retângulo vermelho não foi encontrado na imagem!"
                )
                await update.message.reply_text(
                    "Envie outra imagem contendo um retângulo vermelho válido!"
                )
                return {"status": False}
        except KeyError:  # if not msg key in the json
            new_image_base_rectangle_positions = (
                f'{json["x"]} {json["y"]} {json["h"]} {json["w"]}'
            )
            new_image_base = basename(image_base)  # get the filename
            query_response = update_raffle(
                name=raffle_name,
                user_id=user_id,
                chat_id=chat_id,
                new_image_base=f"{new_image_base}",
                new_image_base_rectangle_positions=new_image_base_rectangle_positions,
            )  # update

            if not query_response["status"]:  # error
                await update.message.reply_text(query_response["msg"])
                return {"status": False}
            else:
                return {"status": True}
