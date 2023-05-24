import os
import telegram
from telegram import Update
from telegram.ext import Updater, MessageHandler, filters, ApplicationBuilder, CommandHandler, ContextTypes

#https://stackoverflow.com/a/1039737
import shutil

# debugging
from icecream import ic

# token for bot
from config import TOKEN

bot = telegram.Bot(TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    starttext = """
Send a .zip archive with your latex project.
It has to contain at least two files:

1. `ANY_NAME.tex`
2. `ANY_NAME_old.tex`

It is important to have a traling `_old` in the old file. 

Bot will do the rest and after some time send you a `diff.pdf` in response.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=starttext
    )

def makediffPDF(zipfile, folder):
    """
        zipfile --- name of the .zip
        folder --- name of the folder where .zip is located
    """
    pwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(folder)
    os.system('unzip -o ' + zipfile)
    # go to the folder where old.tex is located
    os.chdir(os.path.dirname(os.popen('find . -name "*_old.tex"').read()))

    oldfile = os.popen('find . -name "*_old.tex"').read()
    oldfile = oldfile.replace('\n', '')
    newfile = oldfile.replace('_old.tex', '.tex')

    ic(oldfile, newfile)

    os.system('latexdiff ' + oldfile + ' ' + newfile + ' > diff.tex')
    os.system('latex -interaction=nonstopmode diff')
    os.system('bibtex diff')
    os.system('latex -interaction=nonstopmode diff')
    os.system('latex -interaction=nonstopmode diff')
    os.system('pdflatex -interaction=nonstopmode diff')

    os.chdir(pwd)

def downloader(update, context):
    chat_id=update.effective_chat.id
    folder = 'zips/' + str(chat_id)
    if not os.path.exists(folder):
        os.mkdir(folder)
    zipfile_path = folder + '/paper.zip'
    context.bot.get_file(update.message.document).download(custom_path=zipfile_path)
    zipfile = 'paper.zip'
    makediffPDF(zipfile, folder)
    # send diff.pdf
    # https://www.codegrepper.com/code-examples/python/python-telegram-bot+send+file
    path_to_diff = os.popen('find . -name "diff.pdf"').read()
    path_to_diff = path_to_diff.replace('\n', '')
    context.bot.send_document(chat_id=chat_id, document=open(path_to_diff, 'rb'))
    # clean up
    shutil.rmtree(folder)

if __name__ == '__main__':
    #zipfile = 'test_latex.zip'
    #makediffPDF(zipfile)
    #updater = Updater(TOKEN)
    #updater.dispatcher.add_handler(MessageHandler(filters.document, downloader))
    #updater.start_polling()
    #updater.idle()

    application = ApplicationBuilder().token(token=TOKEN).build()
    start_handler = CommandHandler('start', start)
    
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Document, downloader))

    application.run_polling()
