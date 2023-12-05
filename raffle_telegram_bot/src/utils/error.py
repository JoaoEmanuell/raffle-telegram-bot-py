from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def error(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Error interno ao executar ação, avise ao desenvolvedor do bot!"
    )
    return ConversationHandler.END
