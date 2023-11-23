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


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete the raffle"""
    message = "Informe o nome da rifa que será deletada"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

    return RAFFLE_NAME


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    await update.message.reply_text(
        f"Certo, a rifa '{response}' foi deletada com sucesso\!",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return ConversationHandler.END  # end


def create_delete_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete", delete_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
