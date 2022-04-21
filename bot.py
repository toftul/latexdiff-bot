import os
import telegram
from telegram.ext import Updater, MessageHandler, Filters

#https://stackoverflow.com/a/1039737
import shutil

# debugging
from icecream import ic

# token for bot
from config import TOKEN

bot = telegram.Bot(TOKEN)

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
    # clean up
    shutil.rmtree(folder)

if __name__ == '__main__':
    #zipfile = 'test_latex.zip'
    #makediffPDF(zipfile)
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.document, downloader))
    updater.start_polling()
    updater.idle()
