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

from ..utils import cancel
from ..db import create_raffle, update_raffle

RAFFLE_NAME = 1
RAFFLE_NUMBERS = 2


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create a new raffle"""
    message = "Informe o nome da rifa (até 70 carácteres)"

    await update.message.reply_text(message)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    user_id = context._user_id
    chat_id = context._chat_id
    username = update.effective_user.username

    context.user_data["raffle_name"] = name  # save the raffle_name in the context

    query_response = create_raffle(
        name=name,
        user_id=user_id,
        chat_id=chat_id,
        username=username,
        publishers="",
        numbers=1,
        marked_numbers="",
    )

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        await update.message.reply_text("Informe outro nome para a rifa!")
        return RAFFLE_NAME  # Await

    await update.message.reply_text(
        f"Certo, o nome da rifa é: '{name}'\nAgora informe a quantidade de números dela",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return RAFFLE_NUMBERS  # Await


async def raffle_numbers_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    try:
        numbers = int(response)
    except ValueError:
        await update.message.reply_text(
            f"A quantidade informada é inválida, informe novamente com uma quantidade válida\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        raffle_name = context.user_data["raffle_name"]
        user_id = context._user_id
        chat_id = context._chat_id

        print(f"RAFFLE NAME: {raffle_name}")
        print(chat_id, user_id)

        query_response = update_raffle(
            name=raffle_name, user_id=user_id, chat_id=chat_id, new_numbers=numbers
        )

        if not query_response["status"]:
            await update.message.reply_text(query_response["msg"])
            await update.message.reply_text("Informe outro quantidade para a rifa!")
            return RAFFLE_NUMBERS  # Await

        await update.message.reply_text(
            f"O número de elementos da rifa é: {numbers}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await update.message.reply_text(
            f"Rifa criada com sucesso\!", parse_mode=ParseMode.MARKDOWN_V2
        )

        # End
        return ConversationHandler.END


def create_new_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("new", new_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_NUMBERS: [MessageHandler(TEXT & ~COMMAND, raffle_numbers_response)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
