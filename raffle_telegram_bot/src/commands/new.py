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

RAFFLE_NAME = 1
RAFFLE_NUMBERS = 2


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create a new raffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    await update.message.reply_text(
        f"Certo, o nome da rifa é: {response}\nAgora informe a quantidade de números dela",
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
