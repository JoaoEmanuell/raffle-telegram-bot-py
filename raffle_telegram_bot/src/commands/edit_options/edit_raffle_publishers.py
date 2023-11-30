from typing import Callable
from telegram import Update
from telegram.ext import (
    ContextTypes,
)


async def edit_raffle_publishers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raffle: dict,
    update_raffle: Callable,
) -> None:
    response = update.message.text.strip()
    new_raffle_publishers = response.replace("@", "")  # remove the @
    raffle_name = raffle["name"]
    chat_id = context._chat_id
    user_id = context._user_id

    query_response = update_raffle(
        name=raffle_name,
        user_id=user_id,
        chat_id=chat_id,
        new_publishers=new_raffle_publishers,
    )  # update

    if not query_response["status"]:  # error
        await update.message.reply_text(query_response["msg"])
        return {"status": False}
    else:
        return {"status": True}
