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

from ..utils import cancel
from ..db import create_raffle, update_raffle, read_raffle
from src.utils import generate_raffle_image

RAFFLE_NAME = 1
RAFFLE_NUMBERS = 2
RAFFLE_PUBLISHERS = 3


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create a new raffle"""
    message = "Informe o nome da rifa (até 70 carácteres)"

    await update.message.reply_text(message)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    user_id = context._user_id
    chat_id = context._chat_id
    username = update.effective_user.username

    context.user_data["raffle_name"] = name  # save the raffle_name in the context

    query_response = create_raffle(
        name=name,
        user_id=user_id,
        chat_id=chat_id,
        username=username,
        publishers="",
        numbers=1,
        marked_numbers="",
    )

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        await update.message.reply_text("Informe outro nome para a rifa!")
        return RAFFLE_NAME  # Await

    await update.message.reply_text(
        f"Certo, o nome da rifa é: '{name}'\nAgora informe a quantidade de números dela",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return RAFFLE_NUMBERS  # Await


async def raffle_numbers_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    try:
        numbers = int(response)
    except ValueError:
        await update.message.reply_text(
            f"A quantidade informada é inválida, informe novamente com uma quantidade válida\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        raffle_name = context.user_data["raffle_name"]
        user_id = context._user_id
        chat_id = context._chat_id

        print(f"RAFFLE NAME: {raffle_name}")
        print(chat_id, user_id)

        query_response = update_raffle(
            name=raffle_name, user_id=user_id, chat_id=chat_id, new_numbers=numbers
        )

        if not query_response["status"]:
            await update.message.reply_text(query_response["msg"])
            await update.message.reply_text("Informe outro quantidade para a rifa!")
            return RAFFLE_NUMBERS  # Await

        await update.message.reply_text(
            f"O número de elementos da rifa é: {numbers}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await update.message.reply_text(
            f"Agora informe os usuários que podem editar a rifa, basta apenas mencioná-los!"
        )

        # End
        return RAFFLE_PUBLISHERS


async def raffle_publishers_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    publishers = response.strip().replace("@", "")
    raffle_name = context.user_data["raffle_name"]
    user_id = context._user_id
    chat_id = context._chat_id

    query_response = update_raffle(
        name=raffle_name, user_id=user_id, chat_id=chat_id, new_publishers=publishers
    )

    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        await update.message.reply_text("Informe usuários válidos!")
        return RAFFLE_PUBLISHERS

    await update.message.reply_text("Rifa criada com sucesso!")

    query_response = read_raffle(name=raffle_name, user_id=user_id, chat_id=chat_id)
    if not query_response["status"]:
        await update.message.reply_text(query_response["msg"])
        return ConversationHandler.END
    else:
        raffle = query_response["msg"]
        marked_numbers = str(raffle["marked_numbers"]).split(" ")
        image_path = generate_raffle_image(raffle["numbers"], marked_numbers)
        await update.message.reply_photo(image_path)
        await update.message.reply_text(
            "Caso você deseje usar uma imagem como modelo da rifa, você pode usar o comando */edit* e selecionar para colocar uma nova imagem como modelo base.", 
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        remove(image_path)

    return ConversationHandler.END


def create_new_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("new", new_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_NUMBERS: [MessageHandler(TEXT & ~COMMAND, raffle_numbers_response)],
            RAFFLE_PUBLISHERS: [
                MessageHandler(TEXT & ~COMMAND, raffle_publishers_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
