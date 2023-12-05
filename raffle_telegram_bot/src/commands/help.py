from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command, list the bot commands"""
    commands = [
        "*/new* Cria uma nova rifa",
        "*/add* Adicione números marcados a rifa",
        "*/list* Lista as rifas criadas no chat",
        "*/listMe* Lista as rifas criadas pelo usuário",
        "*/edit* Edita as informações da rifa",
        "*/show* Exibe a imagem da rifa",
        "*/raffle* Inicia o sorteio da rifa",
        "*/deleteNumber* Delete um número marcado da rifa",
        "*/delete* Deleta a rifa",
        "*/cancel* Cancela a operação que está sendo realizada no momento",
    ]
    message = ""
    for command in commands:
        message = f"{message}{command}\n"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
