from pathlib import Path
from os import mkdir, remove
from os.path import exists

BASE_DIR = Path(__file__).resolve()
save_path = BASE_DIR.parent.parent.parent
save_base_image_path = f"{save_path}/database/base_raffles_image"

# create the dir if not exists

if not exists(save_base_image_path):
    mkdir(save_base_image_path)

from uuid import uuid4

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import TEXT, COMMAND, PHOTO
from telegram.constants import ParseMode

from requests import get

from ..utils import cancel
from ..db import read_raffle, update_raffle

from .edit_options import (
    edit_raffle_name,
    edit_raffle_publishers,
    edit_raffle_numbers,
    edit_raffle_image_base,
)

RAFFLE_NAME = 1
EDIT_ACTION = 2
ACTION_EDIT_RAFFLE_NAME = 3
ACTION_EDIT_RAFFLE_PUBLISHERS = 4
ACTION_EDIT_NUMBERS = 5
ACTION_EDIT_IMAGE_BASE = 6


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit raffle infos"""
    message = "Informe o nome da rifa"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return RAFFLE_NAME  # Await


async def raffle_name_response(update: Update, context: CallbackContext) -> int:
    # get the raffle
    response = update.message.text

    raffle_name = response.strip()
    chat_id = context._chat_id
    user_id = context._user_id

    raffle_infos = read_raffle(name=raffle_name, chat_id=chat_id, user_id=user_id)

    if not raffle_infos["status"]:  # error
        await update.message.reply_text(
            "Rifa não existe ou não pertence a você, certifique\-se que a rifa é sua antes de edita\-lá\!\nUse o comando */listMe* para listar as rifas criadas por você\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        await update.message.reply_text(
            "Informe o nome de uma rifa válida ou use */cancel* para cancelar a operação\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return RAFFLE_NAME
    else:
        context.user_data["raffle_name"] = raffle_infos["msg"]["name"]
        context.user_data["raffle"] = raffle_infos["msg"]
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
                        f"Editores atuais: {raffle['publishers']}",
                        "Informe os nomes dos novos editores da rifa, separados por espaço",
                    ],
                },
                3: {
                    "action": ACTION_EDIT_NUMBERS,
                    "messages": [
                        "Informe a nova quantidade de números da rifa",
                        f"Quantidade atual: {raffle['numbers']}",
                    ],
                },
                4: {
                    "action": ACTION_EDIT_IMAGE_BASE,
                    "messages": ["Envie a nova imagem modelo da rifa"],
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


async def action_edit_image_base_response(
    update: Update, context: CallbackContext
) -> int:
    if update.message.photo:
        # Get the list of photos size
        photo_sizes = update.message.photo

        # Get the photo object in the best resolution
        largest_photo = photo_sizes[-1]

        # Get the id
        file_id = largest_photo.file_id

        # Use the ID to get the file data
        file = await context.bot.get_file(file_id)
        # Get the path to image in the telegram api
        file_api_path = file.file_path
        content = get(file_api_path).content  # get the byte contents
        image_name = f"{save_base_image_path}/{uuid4()}.jpg"
        with open(image_name, "wb") as image:  # write the image in server
            image.write(content)  # write

        # get the red rectangle area

        edit_raffle_response = await edit_raffle_image_base(
            update=update,
            context=context,
            raffle=context.user_data["raffle"],
            image_base=image_name,
            update_raffle=update_raffle,
        )

        if not edit_raffle_response["status"]:  # error
            return ACTION_EDIT_IMAGE_BASE
        else:
            # delete old image
            old_image = context.user_data["raffle"]["image_base"]
            try:
                remove(f"{save_base_image_path}/{old_image}")
            except FileNotFoundError:
                pass
            finally:
                await update.message.reply_text("Imagem recebida e salva com sucesso!")
                return ConversationHandler.END  # end
    else:
        update.message.reply_text("Imagem inválida")
        update.message.reply_text("Envie uma imagem válida")
        return ACTION_EDIT_IMAGE_BASE


def create_edit_command_handle() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("edit", edit_command)],
        states={
            RAFFLE_NAME: [MessageHandler(TEXT & ~COMMAND, raffle_name_response)],
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
            ACTION_EDIT_IMAGE_BASE: [
                MessageHandler(PHOTO, action_edit_image_base_response)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
