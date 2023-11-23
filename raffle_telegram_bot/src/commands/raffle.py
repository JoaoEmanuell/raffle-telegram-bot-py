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
NUMBERS_FOR_RAFFLE = 2


async def raffle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the raffle"""
    message = "Informe o nome da rifa que será sorteada"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

    return RAFFLE_NAME


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    await update.message.reply_text(
        f"Informe a quantidade de números que serão sorteados",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return NUMBERS_FOR_RAFFLE


async def numbers_for_raffle_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    try:
        number_for_raffle = int(response)
    except ValueError:
        await update.message.reply_text(
            f"O valor informado é inválido, informe um valor válido\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            f"Sorteio realizado\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        return ConversationHandler.END


def create_raffle_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("raffle", raffle_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            NUMBERS_FOR_RAFFLE: [
                MessageHandler(TEXT & ~COMMAND, numbers_for_raffle_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
