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

from ..utils import get_raffle_name, get_raffle_username, cancel
from ..db import read_raffle, update_raffle

from .edit_options import edit_raffle_name, edit_raffle_publishers, edit_raffle_numbers

RAFFLE_NAME = 1
RAFFLE_USERNAME = 2
EDIT_ACTION = 3
ACTION_EDIT_RAFFLE_NAME = 4
ACTION_EDIT_RAFFLE_PUBLISHERS = 5
ACTION_EDIT_NUMBERS = 6
ACTION_EDIT_IMAGE_MODEL = 7


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit raffle infos"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


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
        actions = [
            "*1* Nome da rifa",
            "*2* Editores da rifa",
            "*3* Quantidade de números da rifa",
            "*4* Imagem modelo da rifa",
        ]
        message = ""
        for action in actions:
            message = f"{message}{action}\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
        await update.message.reply_text(
            "Informe o número do que você deseja editar na rifa!"
        )
        return EDIT_ACTION


async def edit_action_response(update: Update, context: CallbackContext) -> int:
    response = update.message.text.strip()
    try:
        action_number = int(response)
    except ValueError:
        await update.message.reply_text("Informe uma opção válida!")
        return EDIT_ACTION  # Await
    else:
        # validate if action is valid
        if action_number < 1 or action_number > 4:
            await update.message.reply_text("Informe uma opção válida!")
            return EDIT_ACTION  # Await
        else:
            raffle = context.user_data["raffle"]
            actions = {
                1: {
                    "action": ACTION_EDIT_RAFFLE_NAME,
                    "messages": ["Informe o novo nome da rifa"],
                },
                2: {
                    "action": ACTION_EDIT_RAFFLE_PUBLISHERS,
                    "messages": [
                        "Informe os nomes dos novos editores da rifa, separados por espaço",
                        f"Editores atuais: {raffle['publishers']}",
                    ],
                },
                3: {
                    "action": ACTION_EDIT_NUMBERS,
                    "messages": [
                        "Informe a nova quantidade de números da rifa",
                        f"Quantidade atual: {raffle['numbers']}",
                    ],
                },
            }

            action = actions[action_number]
            action_messages = action["messages"]
            action_event = action["action"]
            for message in action_messages:
                await update.message.reply_text(message)

            return action_event  # await


async def action_edit_raffle_name_response(
    update: Update, context: CallbackContext
) -> int:
    raffle = context.user_data["raffle"]

    edit_raffle_response = await edit_raffle_name(
        update=update,
        context=context,
        raffle=raffle,
        update_raffle=update_raffle,
        read_raffle=read_raffle,
    )

    if not edit_raffle_response["status"]:  # error
        await update.message.reply_text("Informe um nome válido!")
        return ACTION_EDIT_RAFFLE_NAME
    else:  # success
        await update.message.reply_text("Alteração realizada com sucesso")
        return ConversationHandler.END  # end


async def action_edit_raffle_publishers_response(
    update: Update, context: CallbackContext
) -> int:
    raffle = context.user_data["raffle"]

    edit_raffle_response = await edit_raffle_publishers(
        update=update,
        context=context,
        raffle=raffle,
        update_raffle=update_raffle,
    )

    if not edit_raffle_response["status"]:  # error
        await update.message.reply_text("Informe nomes de editores válidos!")
        return ACTION_EDIT_RAFFLE_PUBLISHERS
    else:  # success
        await update.message.reply_text("Alteração realizada com sucesso")
        return ConversationHandler.END  # end


async def action_edit_raffle_numbers_response(
    update: Update, context: CallbackContext
) -> int:
    raffle = context.user_data["raffle"]

    edit_raffle_response = await edit_raffle_numbers(
        update=update,
        context=context,
        raffle=raffle,
        update_raffle=update_raffle,
    )

    if not edit_raffle_response["status"]:  # error
        await update.message.reply_text("Informe uma quantidade válida!")
        return ACTION_EDIT_NUMBERS
    else:  # success
        await update.message.reply_text("Alteração realizada com sucesso")
        return ConversationHandler.END  # end


def create_edit_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("edit", edit_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
            RAFFLE_USERNAME: [
                MessageHandler(TEXT & ~COMMAND, raffle_username_response)
            ],
            EDIT_ACTION: [MessageHandler(TEXT & ~COMMAND, edit_action_response)],
            ACTION_EDIT_RAFFLE_NAME: [
                MessageHandler(TEXT & ~COMMAND, action_edit_raffle_name_response)
            ],
            ACTION_EDIT_RAFFLE_PUBLISHERS: [
                MessageHandler(TEXT & ~COMMAND, action_edit_raffle_publishers_response)
            ],
            ACTION_EDIT_NUMBERS: [
                MessageHandler(TEXT & ~COMMAND, action_edit_raffle_numbers_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
