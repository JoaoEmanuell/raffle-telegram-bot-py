from typing import Callable
from telegram import Update
from telegram.ext import (
    ContextTypes,
)


async def edit_raffle_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raffle: dict,
    update_raffle: Callable,
    read_raffle: Callable,
) -> None:
    response = update.message.text.strip()
    new_raffle_name = response
    raffle_name = raffle["name"]
    chat_id = context._chat_id
    user_id = context._user_id

    # verify if raffle exists

    query_response = read_raffle(name=new_raffle_name, user_id=user_id, chat_id=chat_id)

    if not query_response["status"]:  # raffle not exists
        query_response = update_raffle(
            name=raffle_name, user_id=user_id, chat_id=chat_id, new_name=new_raffle_name
        )  # update

        if not query_response["status"]:  # error
            await update.message.reply_text(query_response["msg"])
            return {"status": False}
        else:
            return {"status": True}
    else:
        await update.message.reply_text("Rifa já existe!")
        return {"status": False}
