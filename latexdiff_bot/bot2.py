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

from makediff import (
    extract,
    get_main_tex_files,
    get_image_paths,
    find_changed_images,
    make_all_collages,
    latexdiffpdf
)
from settings import (
    load_json_file,
    write_json_file
)
from icecream import ic
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# token for bot
from config import TOKEN

SEND_NEW_FILE, SEND_OLD_FILE, SELECT_NEW_MAIN_TEX, SELECT_OLD_MAIN_TEX = range(4)

# to rename all files uniformly
DEFAULT_NEW_TEX = 'main_new.tex'
DEFAULT_OLD_TEX = 'main_old.tex'

DEFAULT_OLD_ZIP = 'old.zip'
DEFAULT_NEW_ZIP = 'new.zip'

DEFAULT_NEW_DIR = 'new'
DEFAULT_OLD_DIR = 'old'

USER_CONFIG_NAME = 'user_settings.json'
USER_DATA_DIR = 'user_data'

DIFF_TEX_NAME = 'diff.tex'
DIFF_PDF_NAME = DIFF_TEX_NAME.rsplit('.', 1)[0] + '.pdf'


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    helptext = """
*Welcome to the LaTeX Diff Bot\!*

This bot allows you to generate a LaTeX diff file by comparing two versions of a LaTeX document and receive a PDF with the highlighted changes using [latexdiff](https://www.overleaf.com/learn/latex/Articles/Using_Latexdiff_For_Marking_Changes_To_Tex_Documents)\.

Here's how you can use the bot:

1\. Send /start to begin the interaction\.
2\. Upload the original LaTeX project by sending a single `.tex` file or an entire `.zip`\.
3\. If there is an ambiguity which file is the main document you will be promted to select one\.
4\. Upload the old version \(`.tex` or `.zip`\)\.
5\. If there is an ambiguity which file is the main document you will be promted to select one\.
6\. The bot will generate a LaTeX diff file and process it\.
7\. Once the diff file is processed, the bot will send you a PDF with the changes highlighted\.

Project page: 
[gh/toftul/latexdiff\-bot](https://github.com/toftul/latexdiff-bot)

Created by [Ivan Toftul](tg://user?id=63688320)
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=helptext,
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    starttext = '''
Send me a `.tex` or `.zip` of your current latex project
    '''
    keyboard = [["/start", "/help"]]

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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=starttext,
        reply_markup=keyboard,
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )
    return SEND_NEW_FILE


async def do_latexdiff_and_collage(working_dir, chat_id):
    touch_images = True
    config_json = load_json_file(USER_CONFIG_NAME)
    touch_images = False
    if str(chat_id) in config_json:
        touch_images = config_json[str(chat_id)]['touch_images']

    
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
    

# async def ask_for_new_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     working_dir = os.path.join(USER_DATA_DIR, str(chat_id))

#     query = update.callback_query
#     await query.answer()
#     new_main_tex_options = get_main_tex_files(
#         directory=os.path.join(working_dir, DEFAULT_NEW_DIR)
#     )
#     keyboard = [[]]
#     for new_main_tex_option in enumerate(new_main_tex_options):
#         keyboard[0].append(InlineKeyboardButton(new_main_tex_option))

#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await query.edit_message_text(
#         text='It seems that there are more then one main `.tex` files\. Select the one you wish to compare',
#         parse_mode=constants.ParseMode.MARKDOWN_V2,
#         reply_markup=reply_markup
#     )

# async def ask_for_new_main_tex2(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     working_dir = os.path.join(USER_DATA_DIR, str(chat_id))

#     new_main_tex_options = get_main_tex_files(
#         directory=os.path.join(working_dir, DEFAULT_NEW_DIR)
#     )
#     keyboard = [[]]
#     for new_main_tex_option in enumerate(new_main_tex_options):
#         keyboard[0].append(InlineKeyboardButton(new_main_tex_option))
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(
#         text='It seems that there are more then one main `.tex` files\. Select the one you wish to compare',
#         parse_mode=constants.ParseMode.MARKDOWN_V2,
#         reply_markup=reply_markup
#     )


async def mark_new_main_tex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    chosen_new_main_tex = query.data
    path_to_chosen_new_main_tex = os.path.join(working_dir, DEFAULT_NEW_DIR, chosen_new_main_tex)
    # rename
    os.rename(
        src=path_to_chosen_new_main_tex,
        dst=os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX)
    )
    await query.edit_message_text(
        text='''Understood\! Now send the old version \(`tex` or `zip`\)''',
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
    # rename
    os.rename(
        src=path_to_chosen_old_main_tex,
        dst=os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX)
    )
    await query.edit_message_text(
        text='''Got you\! Making `diff.pdf` now\.\.\.''',
        parse_mode=constants.ParseMode.MARKDOWN_V2
    )
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text='''Got you\! Making `diff.pdf` now\.\.\.''',
    #     parse_mode=constants.ParseMode.MARKDOWN_V2
    # )
    # DO THE DIFF PDF
    #################
    await do_latexdiff_and_collage(working_dir=working_dir, chat_id=chat_id)
    path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
    await context.bot.send_document(
        chat_id=chat_id,
        document=open(path_to_diff, 'rb')
    )
    # clean up
    shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
    shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

    # start over
    return SEND_NEW_FILE


async def treat_old_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    if os.path.exists(os.path.join(working_dir, DEFAULT_OLD_DIR)):
        shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

    file = update.message.document

    if file.file_name.endswith('.tex'):
        # download file
        old_tex_path = os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX)
        TheFile = await context.bot.get_file(
            update.message.document.file_id
        )
        await TheFile.download_to_drive(
            custom_path=old_tex_path
        )

        # DO THE DIFF PDF
        #################
        await do_latexdiff_and_collage(working_dir=working_dir)
        path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
        await context.bot.send_document(
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
        TheFile = await context.bot.get_file(
            update.message.document.file_id
        )
        await TheFile.download_to_drive(
            custom_path=old_zip_path
        )
        old_dir_path = os.path.join(working_dir, DEFAULT_OLD_DIR)
        extract(
            path_to_zip=old_zip_path, 
            target_dir=old_dir_path
        )
        main_tex_files = get_main_tex_files(
            directory=old_dir_path
        )
        if len(main_tex_files) > 1:
            keyboard = [[]]
            for old_main_tex_option in main_tex_files:
                keyboard[0].append(InlineKeyboardButton(text=old_main_tex_option, callback_data=old_main_tex_option))
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text='It seems that there are more then one main `.tex` files\. Select the one you wish to compare',
                parse_mode=constants.ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
            return SELECT_OLD_MAIN_TEX
        elif len(main_tex_files) == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Sorry, I could not find any `.tex` file with `\documentclass` in it\. Try another one',
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
            return SEND_OLD_FILE
        else:
            os.rename(
                src=os.path.join(working_dir, DEFAULT_OLD_DIR, main_tex_files[0]),
                dst=os.path.join(working_dir, DEFAULT_OLD_DIR, DEFAULT_OLD_TEX)
            )
            # DO THE DIFF PDF
            #################
            await do_latexdiff_and_collage(working_dir=working_dir, chat_id=chat_id)
            path_to_diff = os.path.join(working_dir, DEFAULT_NEW_DIR, DIFF_PDF_NAME)
            await context.bot.send_document(
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
    working_dir = os.path.join(USER_DATA_DIR, str(chat_id))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    # clean up
    if os.path.exists(os.path.join(working_dir, DEFAULT_NEW_DIR)):
        shutil.rmtree(os.path.join(working_dir, DEFAULT_NEW_DIR))
    if os.path.exists(os.path.join(working_dir, DEFAULT_OLD_DIR)):
        shutil.rmtree(os.path.join(working_dir, DEFAULT_OLD_DIR))

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
            text='Got it\. Now send the old version \(`tex` or `zip`\)',
            parse_mode=constants.ParseMode.MARKDOWN_V2
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
            keyboard = [[]]
            for new_main_tex_option in main_tex_files:
                keyboard[0].append(InlineKeyboardButton(text=new_main_tex_option, callback_data=new_main_tex_option))
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text='It seems that there are more then one main `.tex` files\. Select the one you wish to compare',
                parse_mode=constants.ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
            return SELECT_NEW_MAIN_TEX
        elif len(main_tex_files) == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Sorry, I could not find any `.tex` file with `\documentclass` in it\. Try another one',
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
            return SEND_NEW_FILE
        else:
            os.rename(
                src=os.path.join(working_dir, DEFAULT_NEW_DIR, main_tex_files[0]),
                dst=os.path.join(working_dir, DEFAULT_NEW_DIR, DEFAULT_NEW_TEX)
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='''Got it\! Now send the old version \(`tex` or `zip`\)''',
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
            return SEND_OLD_FILE

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(token=TOKEN).build()

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)

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
                CallbackQueryHandler(
                    mark_new_main_tex
                )
            ],
            SEND_OLD_FILE: [
                MessageHandler(
                    filters=filters.Document.ALL,
                    callback=treat_old_file
                )
            ],
            SELECT_OLD_MAIN_TEX:[
                CallbackQueryHandler(
                    mark_old_main_tex
                )
            ],
        },
        #conversation_timeout=300,  # [s]
        fallbacks=[start_handler]
    )

    application.add_handler(conv_handler)
    application.add_handler(help_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
