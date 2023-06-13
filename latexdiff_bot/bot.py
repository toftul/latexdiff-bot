import os
import json
import shutil
from telegram import (
    Update,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Bot,
    constants
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

from findmain import find_main_tex
from pydiff import do_pydiff, extract

from settings import *

from icecream import ic
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# token for bot
from config import TOKEN

SEND_NEW_FILE, SEND_OLD_FILE, SELECT_NEW_MAIN_TEX, SELECT_OLD_MAIN_TEX = range(4)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MESSAGE_HELP_TEXT,
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["/start", "/settings", "/help", "/cancel"]]

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    # create user data folder is not exits
    if not os.path.exists(USER_DATA_DIR):
        os.mkdir(USER_DATA_DIR)
    # clean user folder for a clean start
    if os.path.exists(os.path.join(USER_DATA_DIR, str(update.effective_chat.id))):
        shutil.rmtree(os.path.join(USER_DATA_DIR, str(update.effective_chat.id)))

    # clean user data if any
    context.user_data.clear()

    # put default settings if never done
    chat_id = update.effective_chat.id
    config_json = load_json_file(USER_CONFIG_NAME)
    if not str(chat_id) in config_json:
        # if first time, set default settings
        config_json[str(chat_id)] = DEFAULT_USER_SETTINGS
        write_json_file(USER_CONFIG_NAME, config_json)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MESSAGE_START_TEXT,
        reply_markup=keyboard,
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )
    return SEND_NEW_FILE


async def cancel(update: Update, context:ContextTypes.DEFAULT_TYPE):
    # clean user folder for a clean start
    if os.path.exists(os.path.join(USER_DATA_DIR, str(update.effective_chat.id))):
        shutil.rmtree(os.path.join(USER_DATA_DIR, str(update.effective_chat.id)))

    # clean user data if any
    context.user_data.clear()

    update.message.reply_text(
        text=MESSAGE_CANCEL
    )


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    config_json = load_json_file(USER_CONFIG_NAME)
    if not str(chat_id) in config_json:
        # if first time, set default settings
        config_json[str(chat_id)] = DEFAULT_USER_SETTINGS
        write_json_file(USER_CONFIG_NAME, config_json)

    for i, (setting_name, setting_state) in enumerate(config_json[str(chat_id)].items()):
        if setting_state:
            response_text = SETTINGS_MENU_MESSAGES[i] + SETTINGS_MENU_ON_ADDTION
        else:
            response_text = SETTINGS_MENU_MESSAGES[i] + SETTINGS_MENU_OFF_ADDTION
        
        keyboard = [
            [
                InlineKeyboardButton("On", callback_data=f"toggle_on_{setting_name}"),
                InlineKeyboardButton("Off", callback_data=f"toggle_off_{setting_name}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=response_text,
            reply_markup=reply_markup
        )


async def handle_toggle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data
    chat_id = update.effective_chat.id
    config_json = load_json_file(USER_CONFIG_NAME)
    current_user_settings = config_json[str(chat_id)]

    setting_name = None
    if 'toggle_on_' in callback_data:
        setting_name = callback_data.split('toggle_on_')[1]
    elif 'toggle_off_' in callback_data:
        setting_name = callback_data.split('toggle_off_')[1]

    if (setting_name is not None) and (setting_name in current_user_settings):
        if 'toggle_on_' in callback_data:
            current_user_settings[setting_name] = True

        if 'toggle_off_' in callback_data:
            current_user_settings[setting_name] = False

        config_json[str(chat_id)] = current_user_settings
        write_json_file(USER_CONFIG_NAME, config_json)
        await query.edit_message_text(
            text=f"{setting_name} is set to {'ON' if current_user_settings[setting_name] else 'OFF'}"
        )


async def do_the_diff_with_user_settings(chat_id, path_to_oldtex, path_to_newtex):
    config_json = load_json_file(USER_CONFIG_NAME)
    if str(chat_id) in config_json:
        imagediff = config_json[str(chat_id)].get('imagediff')
        fast = config_json[str(chat_id)].get('fast')
        compile = config_json[str(chat_id)].get('compile')
    else:
        imagediff = DEFAULT_USER_SETTINGS.get('imagediff')
        fast = DEFAULT_USER_SETTINGS.get('fast')
        compile = DEFAULT_USER_SETTINGS.get('compile')

    path_to_difftex, path_to_diffpdf = do_pydiff(
        path_to_oldtex=path_to_oldtex,
        path_to_newtex=path_to_newtex,
        compile=compile,
        fast=fast,
        imagediff=imagediff
    )
    return path_to_difftex, path_to_diffpdf


async def do_friendly_diff_and_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))

    await update.message.reply_text(
        text=MESSAGE_MAKING_DIFF,
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )

    path_to_difftex, path_to_diffpdf = await do_the_diff_with_user_settings(
        chat_id=chat_id, 
        path_to_oldtex=context.user_data[DEFAULT_OLD_TEX], 
        path_to_newtex=context.user_data[DEFAULT_NEW_TEX]
    )
    if os.path.exists(path_to_diffpdf):
        await update.message.reply_document(
            document=open(path_to_diffpdf, 'rb')
        )
    elif os.path.exists(path_to_difftex):
        await update.message.reply_document(
            document=open(path_to_difftex, 'rb')
        )
    else:
        update.message.reply_text(
            text=MESSAGE_FAILED
        )

    # clean up
    shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
    shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

    # clean user data
    context.user_data.clear()

    await update.message.reply_text(
        text=MESSAGE_START_TEXT,
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )


async def mark_new_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    chosen_new_main_tex = query.data
    path_to_chosen_new_main_tex = os.path.join(working_dir, DEFAULT_NEW_DIR, chosen_new_main_tex)
    context.user_data[DEFAULT_NEW_TEX] = path_to_chosen_new_main_tex

    await query.edit_message_text(
        text=MESSAGE_UNDERSTOOD_NEW,
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )
    return SEND_OLD_FILE


async def mark_old_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    chosen_old_main_tex = query.data
    path_to_chosen_old_main_tex = os.path.join(working_dir, DEFAULT_OLD_DIR, chosen_old_main_tex)
    context.user_data[DEFAULT_OLD_TEX] = path_to_chosen_old_main_tex

    # DO THE DIFF PDF
    await do_friendly_diff_and_clean(update=update, context=context)
    # start over
    return SEND_NEW_FILE



async def treat_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    file = update.message.document
    # if new .tex file is not chosen, do it now
    if context.user_data.get(DEFAULT_NEW_TEX) is None:
        if os.path.exists(os.path.join(working_dir, DEFAULT_NEW_DIR)):
            shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))

        if file.file_name.endswith('.tex'):
            # download file
            new_tex_path = os.path.join(working_dir, DEFAULT_NEW_DIR, file.file_name)
            if not os.path.exists(os.path.dirname(new_tex_path)):
                os.mkdir(os.path.dirname(new_tex_path))

            TheFile = await context.bot.get_file(
                file.file_id
            )
            await TheFile.download_to_drive(
                custom_path=new_tex_path
            )
            context.user_data[DEFAULT_NEW_TEX] = new_tex_path
            await update.message.reply_text(
                text=MESSAGE_UNDERSTOOD_NEW,
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
            return SEND_OLD_FILE
        elif file.file_name.endswith('.zip'):
            new_zip_path = os.path.join(working_dir, DEFAULT_NEW_ZIP)
            TheFile = await context.bot.get_file(
                file.file_id
            )
            await TheFile.download_to_drive(
                custom_path=new_zip_path
            )
            new_dir_path = os.path.join(working_dir, DEFAULT_NEW_DIR)
            extract(
                path_to_zip=new_zip_path,
                target_dir=new_dir_path
            )
            main_tex_files = find_main_tex(
                path_to_dir=new_dir_path
            )
            if len(main_tex_files) > 1:
                keyboard = [[]]
                for main_tex_option in main_tex_files:
                    keyboard[0].append(
                        InlineKeyboardButton(
                            text=main_tex_option,
                            callback_data=main_tex_option
                        )
                    )
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        text=MESSAGE_MORE_THAN_ONE_TEX,
                        parse_mode=constants.ParseMode.MARKDOWN_V2,
                        reply_markup=reply_markup
                    )
                    return SELECT_NEW_MAIN_TEX
            elif len(main_tex_files) == 0:
                await update.message.reply_text(
                    text=MESSAGE_SORRY_NO_TEX,
                    parse_mode=constants.ParseMode.MARKDOWN_V2
                )
                return SEND_NEW_FILE
            else:
                await update.message.reply_text(
                    text=MESSAGE_UNDERSTOOD_NEW,
                    parse_mode=constants.ParseMode.MARKDOWN_V2
                )
                path_to_new_tex_file = os.path.join(working_dir, DEFAULT_NEW_DIR, main_tex_files[0])
                context.user_data[DEFAULT_NEW_TEX] = path_to_new_tex_file
                return SEND_OLD_FILE
    else:
        # if new tex file is selected, not we need to select the old one
        if os.path.exists(os.path.join(working_dir, DEFAULT_OLD_DIR)):
            shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))
        
        if file.file_name.endswith('.tex'):
            # download file
            old_tex_path = os.path.join(working_dir, DEFAULT_OLD_DIR, file.file_name)
            if not os.path.exists(os.path.dirname(old_tex_path)):
                os.mkdir(os.path.dirname(old_tex_path))
            
            TheFile = await context.bot.get_file(
                file.file_id
            )
            await TheFile.download_to_drive(
                custom_path=old_tex_path
            )
            context.user_data[DEFAULT_OLD_TEX] = old_tex_path

            ## DO THE DIFF
            await do_friendly_diff_and_clean(update=update, context=context)
            # start over
            return SEND_NEW_FILE
        elif file.file_name.endswith('.zip'):
            old_zip_path = os.path.join(working_dir, DEFAULT_OLD_ZIP)
            TheFile = await context.bot.get_file(
                file.file_id
            )
            await TheFile.download_to_drive(
                custom_path=old_zip_path
            )
            old_dir_path = os.path.join(working_dir, DEFAULT_OLD_DIR)
            extract(
                path_to_zip=old_zip_path,
                target_dir=old_dir_path
            )
            main_tex_files = find_main_tex(
                path_to_dir=old_dir_path
            )
            if len(main_tex_files) > 1:
                keyboard = [[]]
                for main_tex_option in main_tex_files:
                    keyboard[0].append(
                        InlineKeyboardButton(
                            text=main_tex_option,
                            callback_data=main_tex_option
                        )
                    )
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        text=MESSAGE_MORE_THAN_ONE_TEX,
                        parse_mode=constants.ParseMode.MARKDOWN_V2,
                        reply_markup=reply_markup
                    )
                    return SELECT_OLD_MAIN_TEX
            elif len(main_tex_files) == 0:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=MESSAGE_SORRY_NO_TEX,
                    parse_mode=constants.ParseMode.MARKDOWN_V2
                )
                return SEND_OLD_FILE
            else:
                path_to_old_tex_file = os.path.join(working_dir, DEFAULT_OLD_DIR, main_tex_files[0])
                context.user_data[DEFAULT_OLD_TEX] = path_to_old_tex_file

                ## DO THE DIFF
                await do_friendly_diff_and_clean(update=update, context=context)
                # start over
                return SEND_NEW_FILE


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(token=TOKEN).build()

    start_handler = CommandHandler('start', start)
    cancel_handler = CommandHandler('cancel', cancel)
    help_handler = CommandHandler('help', help)
    settings_handler = CommandHandler('settings', show_settings)
    toggle_query = CallbackQueryHandler(handle_toggle_settings)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            SEND_NEW_FILE: [
                MessageHandler(
                    filters=filters.Document.ALL, 
                    callback=treat_upload
                )
            ],
            SELECT_NEW_MAIN_TEX:[
                CallbackQueryHandler(
                    mark_new_main_tex
                )
            ],
            SEND_OLD_FILE: [
                MessageHandler(
                    filters=filters.Document.ALL,
                    callback=treat_upload
                )
            ],
            SELECT_OLD_MAIN_TEX:[
                CallbackQueryHandler(
                    mark_old_main_tex
                )
            ],
        },
        conversation_timeout=300,  # [s]
        fallbacks=[start_handler, cancel_handler]
    )

    application.add_handler(conv_handler)
    application.add_handler(help_handler)
    application.add_handler(cancel_handler)
    application.add_handler(settings_handler)
    application.add_handler(toggle_query)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
