from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

if __name__ == '__main__':
    from os import getenv
    from dotenv import load_dotenv
    # Run server
    load_dotenv() # load the dotenv

    TOKEN = getenv('TOKEN')

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    app.run_polling()