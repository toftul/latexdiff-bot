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

# SEND_FIRST_FILE, SEND_OLD_ZIP, SEND_OLD_TEX, CHOOSE_MAIN_TEX = range(4)
SEND_NEW_FILE, SEND_OLD_FILE, SELECT_NEW_MAIN_TEX, SELECT_OLD_MAIN_TEX = range(4)

# to rename all files uniformly
DEFAULT_NEW_TEX = 'main_new.tex'
DEFAULT_OLD_TEX = 'main_old.tex'

DEFAULT_OLD_ZIP = 'old.zip'
DEFAULT_NEW_ZIP = 'new.zip'

DEFAULT_NEW_DIR = 'new'
DEFAULT_OLD_DIR = 'old'

USER_CONFIG_NAME = 'config.json'

DIFF_TEX_NAME = 'diff.tex'
DIFF_PDF_NAME = DIFF_TEX_NAME.rsplit('.', 1)[0] + '.pdf'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    starttext = """
Send me a '.tex' or '.zip' of your current latex project.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
    )
    return SEND_NEW_FILE


async def start2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    starttext = """
Send me a '.tex' or '.zip' of your current latex project.
    """
    keyboard = [["/start"]]

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
        reply_markup=keyboard
    )
    return SEND_NEW_FILE


def do_latexdiff_and_collage(working_dir):
    touch_images = True
    config_file = os.path.join(working_dir, USER_CONFIG_NAME)
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            loaded_data = json.load(file)
        touch_images = loaded_data['touch_images']  

    
    dir_new_full = os.path.join(os.getcwd(), working_dir, DEFAULT_NEW_DIR)
    dir_old_full = os.path.join(os.getcwd(), working_dir, DEFAULT_OLD_DIR)

    new_tex_file = os.path.join(dir_new_full, DEFAULT_NEW_TEX)
    old_tex_file = os.path.join(dir_old_full, DEFAULT_OLD_TEX)
    
    if touch_images:
        old_image_paths = get_image_paths(old_tex_file)
        new_image_paths = get_image_paths(new_tex_file)

        changed_images = find_changed_images(old_image_paths, new_image_paths)

        new_image_paths_full = []
        for i in range(len(new_image_paths)):
            new_image_paths_full.append(os.path.join(dir_new_full, new_image_paths[i]))

        old_image_paths_full = []
        for i in range(len(old_image_paths)):
            old_image_paths_full.append(os.path.join(dir_old_full, old_image_paths[i]))

        blank_image_path = os.path.join(os.getcwd(), 'blank.jpg')

        make_all_collages(old_image_paths_full, new_image_paths_full, changed_images, blank_image_path)
    
    # DO THE DIFF PDF
    latexdiffpdf(
        old_tex_file=os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX),
        new_tex_file=os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX),
        dir_new_full=os.path.join(working_dir, DEFAULT_NEW_DIR),
        diff_file=DIFF_TEX_NAME
    )
    

async def mark_new_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = str(chat_id)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    chosen_new_main_tex = update.message.text
    path_to_chosen_new_main_tex = os.path.join(working_dir, DEFAULT_NEW_DIR, chosen_new_main_tex)
    # rename
    os.rename(
        src=path_to_chosen_new_main_tex,
        dst=os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX)
    )
    return SEND_OLD_FILE


async def mark_old_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = str(chat_id)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    chosen_old_main_tex = update.message.text
    path_to_chosen_old_main_tex = os.path.join(working_dir, DEFAULT_OLD_DIR, chosen_old_main_tex)
    # rename
    os.rename(
        src=path_to_chosen_old_main_tex,
        dst=os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX)
    )

    # DO THE DIFF PDF
    #################
    do_latexdiff_and_collage(working_dir=working_dir)
    path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
    context.bot.send_document(
        chat_id=chat_id,
        document=open(path_to_diff, 'rb')
    )
    # clean up
    shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
    shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

    # start over
    return SEND_NEW_FILE


async def treat_old_file(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    working_dir = str(chat_id)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    file = update.message.document

    if file.file_name.endswith('.tex'):
        # download file
        old_tex_path = os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX)
        context.bot.get_file(
            update.message.document.file_id
        ).download_to_drive(custom_path=old_tex_path)

        # DO THE DIFF PDF
        #################
        do_latexdiff_and_collage(working_dir=working_dir)
        path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
        context.bot.send_document(
            chat_id=chat_id,
            document=open(path_to_diff, 'rb')
        )
        # clean up
        shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
        shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

        # start over
        return SEND_NEW_FILE
    elif file.file_name.endswith('.zip'):
        # download file
        old_zip_path = os.path.join(working_dir, DEFAULT_OLD_ZIP)
        context.bot.get_file(
            update.message.document.file_id
        ).download_to_grive(custom_path=old_zip_path)
        old_dir_path = os.path.join(working_dir, DEFAULT_OLD_DIR)
        extract(
            path_to_zip=old_zip_path, 
            target_dir=old_dir_path
        )
        main_tex_files = get_main_tex_files(
            directory=old_dir_path
        )
        if len(main_tex_files) > 1:
            keyboard = [[main_tex_files]]

            reply_keyboard = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=False
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Choose main `.tex` file',
                reply_markup=reply_keyboard
            )
            return SELECT_OLD_MAIN_TEX
        elif len(main_tex_files) == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Sorry, I could not find any `.tex` file with `\documentclass` in it. Try another one.'
            )
            return SEND_OLD_FILE
        else:
            # DO THE DIFF PDF
            #################
            do_latexdiff_and_collage(working_dir=working_dir)
            path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
            context.bot.send_document(
                chat_id=chat_id,
                document=open(path_to_diff, 'rb')
            )
            # clean up
            shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
            shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

            # start over
            return SEND_NEW_FILE

 
async def treat_new_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = str(chat_id)
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    file = update.message.document

    if file.file_name.endswith('.tex'):
        # download file
        new_tex_path = os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX)
        TheFile = await context.bot.get_file(
            update.message.document.file_id
        )
        await TheFile.download_to_drive(custom_path=new_tex_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Got it. Now send the old version (tex or zip).'
        )

        return SEND_OLD_FILE
    elif file.file_name.endswith('.zip'):
        # download file
        new_zip_path = os.path.join(working_dir, DEFAULT_NEW_ZIP)
        #print(context.bot.get_file(update.message.document.file_id))
        TheFile = await context.bot.get_file(
            update.message.document.file_id
        )
        await TheFile.download_to_drive(custom_path=new_zip_path)
        
        new_dir_path = os.path.join(working_dir, DEFAULT_NEW_DIR)
        extract(
            path_to_zip=new_zip_path, 
            target_dir=new_dir_path
        )
        main_tex_files = get_main_tex_files(
            directory=new_dir_path
        )
        if len(main_tex_files) > 1:
            keyboard = [[main_tex_files]]

            reply_keyboard = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=False
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Choose main `.tex` file',
                reply_markup=reply_keyboard
            )
            return SELECT_NEW_MAIN_TEX
        elif len(main_tex_files) == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Sorry, I could not find any `.tex` file with `\documentclass` in it. Try another one.'
            )
            return SEND_NEW_FILE
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Got it. Now send the old version (tex or zip).'
            )
            return SEND_OLD_FILE


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

    start_handler = CommandHandler('start', start2)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            SEND_NEW_FILE: [
                MessageHandler(
                    filters=filters.Document.ALL, 
                    callback=treat_new_file
                )
            ],
            SELECT_NEW_MAIN_TEX:[
                MessageHandler(
                    filters=filters.TEXT,
                    callback=mark_new_main_tex
                )
            ],
            SEND_OLD_FILE: [
                MessageHandler(
                    filters=filters.Document.ALL,
                    callback=treat_old_file
                )
            ],
            SELECT_OLD_MAIN_TEX:[
                MessageHandler(
                    filters=filters.TEXT,
                    callback=mark_old_main_tex
                )
            ],
        },
        #conversation_timeout=300,  # [s]
        fallbacks=[start_handler]
    )

    application.add_handler(conv_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
