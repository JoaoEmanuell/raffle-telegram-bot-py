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

from ..db import read_raffle
from ..utils import (
    cancel,
    get_raffle_name,
    get_raffle_username,
    handler_generate_image,
)

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show raffle"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    """Get the raffle name"""
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
        raffle = raffle_infos["raffle"]  # add raffle to context
        image = await handler_generate_image(raffle)
        await update.message.reply_photo(image)
        remove(image)
        return ConversationHandler.END  # end


def create_show_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("show", show_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
