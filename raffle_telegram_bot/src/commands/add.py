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
NUMBERS_FOR_ADD = 2


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add marked number in the riffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    await update.message.reply_text(
        f"Certo, o nome da rifa é: {response}\nAgora informe os números que você deseja marcar, separado por ','",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return NUMBERS_FOR_ADD  # Await


async def numbers_for_add_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    numbers_list = response.split(",")
    try:
        numbers_list = [int(x) for x in numbers_list]
    except ValueError:
        await update.message.reply_text(
            f"Um dos números informados é inválido, por favor, informe números válidos\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            f"Números: {response}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

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
