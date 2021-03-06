import logging
import os

from datetime import datetime

from thesaurus.dictionary import Dictionary
from thesaurus.translator import Translator, TranslatorBot

# logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

tBot = TranslatorBot(os.environ["TELEGRAM_KEY"])
bot = tBot.bot
chat_translators = {}

@bot.message_handler(commands=['help', 'start', 'info'])
def get_help(message):
    help_info =  f"""/help /start /info - displays the menu \n /identify [iso lang code]- adds the current chat into a list of translators by creating a translator from [iso lang code] to EN \n /identify me- Returns a list of bots currently available for this conversation \n /translate [message] - returns the translation of the message to english"""
   
    bot.reply_to(message, help_info)

@bot.message_handler(commands=['identify'])
def identify(message):
    cid = message.chat.id
    args = tBot.extract_arg(message.text)
    if(len(args) == 1):
        arg = str(args[0])
        if(arg == 'me'):
            try: 
                bot.reply_to(message, f"Translators for {cid}: {chat_translators[cid].dict.language}")
            except KeyError:                
                bot.reply_to(message, f" No Translators for {cid}")
        else:
            t = Translator(Dictionary(arg), os.environ["DEEPL_KEY"])
            chat_translators[cid] = t
            bot.reply_to(message, f"Created translator for {cid} and language {arg}")
    else:
        bot.reply_to(message, "Please pass a second param to initialise the translator")

@bot.message_handler(commands=['translate'])
def translate_message(message):
    cid = message.chat.id
    try:
        t = chat_translators[cid]
        message_text = message.text.replace('/translate','')
        if len(message_text) > 0:
            msg = t.translate_message(message_text, t.dict.language)
            if len(msg) <= 0:
                msg = f"Error translating {message_text}"
            bot.reply_to(message, msg)
        else: 
            bot.reply_to(message, "You need to pass something to be translated")
    except KeyError:
        pass

bot.polling(none_stop=True, interval=3, timeout=10)

