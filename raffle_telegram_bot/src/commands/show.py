from os import remove

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import TEXT, COMMAND
from telegram.constants import ParseMode

from ..db import read_raffle
from ..utils import (
    cancel,
    generate_raffle_image,
    get_raffle_name,
    get_raffle_username,
    personalized_model_image,
)

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show raffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    """Get the raffle name"""
    raffle_infos = await get_raffle_name(update, context, read_raffle)

    if not raffle_infos["status"]:  # error
        return RAFFLE_NAME
    else:
        context.user_data["raffle_name"] = raffle_infos["raffle_name"]
        context.user_data["raffle"] = raffle_infos["raffle"]

        await update.message.reply_text(
            "Informe o nome do usuário a quem a rifa pertence, mencione o usuário!",
        )

        return RAFFLE_USERNAME  # Await


async def raffle_username_response(update: Update, context: CallbackContext) -> int:
    raffle_infos = await get_raffle_username(update, context, read_raffle)

    if not raffle_infos["status"]:
        return RAFFLE_USERNAME
    else:
        raffle = raffle_infos["raffle"]  # add raffle to context
        numbers = int(raffle["numbers"])
        marked_numbers = str(raffle["marked_numbers"]).split(" ")  # transform to a list
        print(raffle)
        image_base = raffle["image_base"]
        image_path = generate_raffle_image(numbers, marked_numbers)
        if image_base != "":
            image_base_rectangle_positions = raffle[
                "image_base_rectangle_positions"
            ].split(
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
            # reply the photo
            await update.message.reply_photo(personalized_image)
            remove(personalized_image)
        else:
            # reply the photo
            await update.message.reply_photo(image_path)
        remove(image_path)
        return ConversationHandler.END  # end


def create_show_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("show", show_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
