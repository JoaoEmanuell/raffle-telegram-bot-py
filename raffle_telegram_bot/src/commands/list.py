from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from src.db import read_all_user_raffle


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command, list the bot commands"""
    user_id = context._user_id
    chat_id = context._chat_id
    query_response = read_all_user_raffle(user_id=user_id, chat_id=chat_id)

    if not query_response["status"]:
        # error
        await update.message.reply_text(query_response["msg"])
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            query_response["msg"], parse_mode=ParseMode.MARKDOWN_V2
        )
        return ConversationHandler.END
