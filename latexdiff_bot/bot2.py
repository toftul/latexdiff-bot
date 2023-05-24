import os
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
    ConversationHandler
)
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# token for bot
from config import TOKEN

SEND_FIRST_FILE, SEND_OLD_ZIP, SEND_OLD_TEX, CHOOSE_MAIN_TEX = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    starttext = """
Send me a `.tex` or `.zip` of your current latex project.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
    )
    return SELECT_FILE

async def downloader(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text

    if text == 'tex':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Thank you for .tex file',
        )
        return SELECT_SECOND_FILE
    elif text == 'zip':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Thank you for .zip file',
        )
        return SELECT_SECOND_FILE

async def start2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    starttext = """
Hello!
    """
    keyboard = [["main.tex", "sm.tex"]]

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
        reply_markup=keyboard
    )

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(token=TOKEN).build()

    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)

    difflatex_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            THIS_IS_TEX_FILE: [

            ],
            THIS_IS_ZIP: [

            ],
            START_AGAIN: [

            ],
        },
        conversation_timeout=300,  # [s]
        fallbacks=[start_handler]
    )

    application.add_handler(start_handler)
    application.add_handler(caps_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
