from random import choice

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
from ..utils import cancel, get_raffle_username, get_raffle_name

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2
NUMBERS_FOR_RAFFLE = 3


async def raffle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the raffle"""
    message = "Informe o nome da rifa que será sorteada"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

    return RAFFLE_NAME


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
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
        context.user_data["username"] = raffle_infos["username"]  # add to context
        context.user_data["raffle"] = raffle_infos["raffle"]  # add raffle to context
        await update.message.reply_text(
            f"Números marcados: {raffle_infos['raffle']['marked_numbers']}"
        )
        await update.message.reply_text(
            "Informe a quantidade de números que você deseja sortear!"
        )
        return NUMBERS_FOR_RAFFLE  # Await


async def numbers_for_raffle_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text

    try:
        number_for_raffle = abs(int(response))
    except ValueError:
        await update.message.reply_text(
            f"O valor informado é inválido, informe um valor válido\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        raffle = context.user_data["raffle"]

        marked_numbers = raffle["marked_numbers"]
        marked_numbers_list = str(marked_numbers).split(" ")

        # Validate if marked numbers list len is less than numbers for raffle

        if marked_numbers == "":  # if not have a marked numbers
            await update.message.reply_text(
                "Não é possível iniciar o sorteio pois a rifa não possui nenhum número marcado\!\nUse o comando */add* para adicionar números marcados a rifa\!",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return ConversationHandler.END
        elif len(marked_numbers_list) < number_for_raffle:
            await update.message.reply_text(
                f"A quantidade de números para serem sorteados é superior a quantidade de números marcados!\nInforme uma nova quantidade!",
            )
            return NUMBERS_FOR_RAFFLE  # Await

        sorted_numbers = []

        # start sort

        for _ in range(number_for_raffle):
            number = choice(marked_numbers_list)
            sorted_numbers.append(int(number))
            marked_numbers_list.remove(number)

        sorted_numbers.sort()  # sort the list

        sorted_numbers = " ".join(map(str, sorted_numbers))  # convert numbers to string

        await update.message.reply_text(
            f"Números vencedores: {sorted_numbers}",
        )

        return ConversationHandler.END


def create_raffle_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("raffle", raffle_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
            NUMBERS_FOR_RAFFLE: [
                MessageHandler(TEXT & ~COMMAND, numbers_for_raffle_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
