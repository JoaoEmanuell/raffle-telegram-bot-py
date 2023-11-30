from typing import Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
)
from telegram.constants import ParseMode


async def get_raffle_username(
    update: Update, context: CallbackContext, read_raffle: Callable
) -> object:
    """get raffle name

    Args:
        update (Update): telegram
        context (CallbackContext): telegram
        read_raffle (Callable): read raffle to access the database

    Returns:
        if raffle exists in chat:
            {
                "status": True,
                "username": str,
                "raffle": object
            }
        else:
            {
                "status": False
            }
    """
    response = update.message.text

    username = response.strip().replace("@", "")  # remove the @
    raffle_name = context.user_data["raffle_name"]
    chat_id = context._chat_id

    query_response = read_raffle(name=raffle_name, username=username, chat_id=chat_id)

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        await update.message.reply_text(
            "Informe o nome do usuário a quem a rifa pertence, ou use */cancel* para cancelar a operação",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return {"status": False}  # Await

    return {"status": True, "username": username, "raffle": query_response["msg"]}
