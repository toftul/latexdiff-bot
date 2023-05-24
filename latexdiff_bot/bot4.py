import os
import json
import shutil
from telegram import (
    Update,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Bot,
)
from telegram.ext import (
    Updater,
    MessageHandler,
    filters,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

from makediff import (
    extract,
    get_main_tex_files,
    get_image_paths,
    find_changed_images,
    make_all_collages,
    latexdiffpdf
)
from icecream import ic
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# token for bot
from config import TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    starttext = """
Send me a '.tex' or '.zip' of your current latex project.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
    )

async def load(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.get_file(update.message.document.file_id).download_to_drive(custom_path='wow.zip')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Downloaded!',
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(token=TOKEN).build()

    start_handler = CommandHandler('start', start)
    
    download_handler = MessageHandler(filters=filters.Document.ALL, callback=load)

    application.add_handler(download_handler)

    application.run_polling()
