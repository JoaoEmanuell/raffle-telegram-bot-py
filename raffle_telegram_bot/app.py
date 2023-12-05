from telegram.ext import ApplicationBuilder, CommandHandler

from src import (
    create_add_command_handle,
    create_delete_number_command_handle,
    create_delete_command_handle,
    create_new_command_handle,
    create_raffle_command_handle,
    help_command,
    create_tables,
    list_command,
    create_show_command_handle,
    list_me_command,
    create_edit_command_handle,
)


if __name__ == "__main__":
    # create tables
    create_tables()

    from os import getenv
    from dotenv import load_dotenv

    load_dotenv()  # load the dotenv

    TOKEN = getenv("TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    # Add the commands

    app.add_handler(create_add_command_handle())  # add
    app.add_handler(create_delete_number_command_handle())  # delete number
    app.add_handler(create_delete_command_handle())  # delete raffle
    app.add_handler(create_new_command_handle())  # new
    app.add_handler(create_raffle_command_handle())  # raffle
    app.add_handler(CommandHandler("help", help_command))  # help
    app.add_handler(CommandHandler("list", list_command))  # list
    app.add_handler(CommandHandler("listme", list_me_command))  # list user raffles
    app.add_handler(create_show_command_handle())  # show
    app.add_handler(create_edit_command_handle())  # edit

    # Run server
    print("Running server")
    app.run_polling()
