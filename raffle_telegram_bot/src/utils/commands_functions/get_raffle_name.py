from typing import Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
)
from telegram.constants import ParseMode


async def get_raffle_name(
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
                "raffle_name": str,
                "raffle": object
            }
        else:
            {
                "status": False
            }
    """
    response = update.message.text

    raffle_name = response.strip()
    chat_id = context._chat_id

    query_response = read_raffle(
        name=raffle_name, chat_id=chat_id
    )  # validate if raffle exists in chat

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        await update.message.reply_text(
            "Rifa não existe no chat, informe o nome de uma rifa presente no chat, use o */list* para listar todas as rifas criadas nesse chat\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return {"status": False}  # Response

    return {"status": True, "raffle_name": raffle_name, "raffle": query_response["msg"]}
