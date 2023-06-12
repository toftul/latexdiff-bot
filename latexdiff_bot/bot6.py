import os
import shutil
import time
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    constants
)

from telegram.ext import (
    MessageHandler,
    filters,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

from settings import (
    load_json_file,
    write_json_file
)

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from config import TOKEN_AGAIN as TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text='Send me your latex project (tex or zip).'
    )

async def start2(update, context):
    # Create a list of commands
    commands = [
        ['/command1', 'Command 1'],
        ['/command2', 'Command 2'],
        ['/command3', 'Command 3']
    ]
    
    # Create a list of button rows
    keyboard = [[InlineKeyboardButton(cmd[1], callback_data=cmd[0])] for cmd in commands]
    
    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the menu message with the keyboard
    await update.message.reply_text('Please select a command:', reply_markup=reply_markup)


async def command1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "You have pressed Command 1"

    await update.message.reply_text(text=text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(
        token=TOKEN
    ).build()

    start_handler = CommandHandler(command='start', callback=start2)

    comm1 = CommandHandler(command='command1', callback=command1)

    #conv_handler = ConversationHandler(
    #    entry_points=[start_handler]
    #)

    # add handlers
    application.add_handler(start_handler)
    application.add_handler(comm1)
    

    # other
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling(timeout=30)