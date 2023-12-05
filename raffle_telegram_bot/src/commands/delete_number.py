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

from ..utils import cancel, get_raffle_name, get_raffle_username, handler_generate_image
from ..db import read_raffle, add_numbers_to_raffle

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2
NUMBERS_FOR_DELETE = 3


async def delete_number_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Delete marked number in the raffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

    return RAFFLE_NAME


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
        context.user_data["username"] = raffle_infos["username"]
        context.user_data["raffle_to_delete"] = raffle_infos[
            "raffle"
        ]  # add raffle to context
        await update.message.reply_text(
            f"Números marcados: {raffle_infos['raffle']['marked_numbers']}"
        )
        await update.message.reply_text(
            "Informe os números que você deseja deletar, separado por espaço"
        )
        return NUMBERS_FOR_DELETE  # Await


async def numbers_for_delete_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    numbers_list = response.split(" ")
    try:
        numbers_list = [int(x) for x in numbers_list]
    except ValueError:
        await update.message.reply_text(
            f"Um dos números informados é inválido, por favor, informe números válidos\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        raffle_to_delete = context.user_data["raffle_to_delete"]

        marked_numbers = str(raffle_to_delete["marked_numbers"]).split(" ")

        # remove to marked numbers

        for number in numbers_list:
            try:
                marked_numbers.remove(str(number))
            except ValueError:
                continue

        # update in database

        raffle_name = context.user_data["raffle_name"]
        chat_id = context._chat_id
        username = context.user_data["username"]
        publisher = update.message.from_user.username

        query_response = add_numbers_to_raffle(
            name=raffle_name,
            chat_id=chat_id,
            username=username,
            publisher=publisher,
            new_marked_numbers=" ".join(marked_numbers),
        )

        if not query_response["status"]:
            await update.message.reply_text(query_response["msg"])
            return NUMBERS_FOR_DELETE  # await
        else:
            await update.message.reply_text(
                "Números apagados com sucesso\nGerando uma nova imagem"
            )
            # generate new image
            raffle = context.user_data["raffle_to_delete"]  # get raffle
            raffle["marked_numbers"] = " ".join(
                marked_numbers
            )  # use the new numbers to generate
            image_path = await handler_generate_image(raffle)
            await update.message.reply_photo(image_path)
            remove(image_path)

        return ConversationHandler.END  # end


def create_delete_number_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("deleteNumber", delete_number_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
            NUMBERS_FOR_DELETE: [
                MessageHandler(TEXT & ~COMMAND, numbers_for_delete_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
