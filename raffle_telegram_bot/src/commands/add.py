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

from ..db import update_raffle, read_raffle
from ..utils import cancel, generate_raffle_image

RAFFLE_NAME = 1
NUMBERS_FOR_ADD = 2


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add marked number in the riffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    context.user_data["raffle_name"] = response.strip()

    raffle_name = context.user_data["raffle_name"]
    user_id = context._user_id
    chat_id = context._chat_id

    query_response = read_raffle(name=raffle_name, user_id=user_id, chat_id=chat_id)

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        return RAFFLE_NAME  # Await
    else:
        await update.message.reply_text(
            f"Certo, o nome da rifa é: {raffle_name}\nAgora informe os números que você deseja marcar, separado por espaço",
            parse_mode=ParseMode.MARKDOWN_V2,
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
        numbers_string = response.strip()
        raffle_name = context.user_data["raffle_name"]
        user_id = context._user_id
        chat_id = context._chat_id

        query_response = update_raffle(
            name=raffle_name,
            user_id=user_id,
            chat_id=chat_id,
            new_marked_numbers=numbers_string,
        )

        if not query_response["status"]:
            await update.message.reply_text(query_response["msg"])
        else:
            await update.message.reply_text(
                f"Números marcados: {numbers_string}",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            raffle = read_raffle(raffle_name, user_id, chat_id)["msg"]
            numbers = int(raffle["numbers"])
            marked_numbers = str(raffle["marked_numbers"]).split(" ")
            # generate new image
            image_path = generate_raffle_image(numbers, marked_numbers)
            await update.message.reply_photo(image_path)
            remove(image_path)

        return ConversationHandler.END  # end


def create_add_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            NUMBERS_FOR_ADD: [
                MessageHandler(TEXT & ~COMMAND, numbers_for_add_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
