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

from ..db import add_numbers_to_raffle, read_raffle
from ..utils import cancel, generate_raffle_image, get_raffle_username, get_raffle_name

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2
NUMBERS_FOR_ADD = 3


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add marked number in the raffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
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
        context.user_data["username"] = raffle_infos["username"]  # add to context
        context.user_data["raffle"] = raffle_infos["raffle"]  # add raffle to context
        await update.message.reply_text(
            "Informe os números que você deseja marcar, separado por espaço"
        )
        return NUMBERS_FOR_ADD  # Await


async def numbers_for_add_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    numbers_list = response.strip().split(" ")
    try:
        numbers_list = [int(x) for x in numbers_list]
    except ValueError:
        await update.message.reply_text(
            f"Um dos números informados é inválido, por favor, informe números válidos\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        raffle_name = context.user_data["raffle_name"]
        chat_id = context._chat_id
        username = context.user_data["username"]

        raffle = context.user_data["raffle"]

        if str(raffle["marked_numbers"]) == "":  # if not have numbers in the raffle
            marked_numbers: list[str] = []
        else:
            marked_numbers = (
                str(raffle["marked_numbers"]).strip().split(" ")
            )  # transform to a list

        # Add numbers to marked numbers

        for number in numbers_list:
            # Validate if numbers exists
            if str(number) in marked_numbers:
                await update.message.reply_text(
                    f"O número {number} já foi adicionado, informe novos números!"
                )
                return NUMBERS_FOR_ADD  # Await
            else:
                marked_numbers.append(str(number))

        sort_marked_numbers = [
            int(x) for x in marked_numbers
        ]  # sort the marked numbers
        sort_marked_numbers.sort()

        marked_numbers = sort_marked_numbers.copy()

        marked_numbers = [str(x) for x in marked_numbers]  # transform in a string list

        publisher = update.message.from_user.username

        # update the raffle
        query_response = add_numbers_to_raffle(
            name=raffle_name,
            username=username,
            chat_id=chat_id,
            publisher=publisher,
            new_marked_numbers=" ".join(marked_numbers),
        )

        if not query_response["status"]:
            await update.message.reply_text(query_response["msg"])
        else:
            # generate new image
            numbers = int(raffle["numbers"])
            image_path = generate_raffle_image(numbers, marked_numbers)
            await update.message.reply_photo(image_path)
            remove(image_path)

    return ConversationHandler.END  # end


def create_add_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
            NUMBERS_FOR_ADD: [
                MessageHandler(TEXT & ~COMMAND, numbers_for_add_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
