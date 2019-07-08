from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import MessageEntity, ParseMode
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_text

from googletrans import Translator

@run_async
def translate(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message # type: Optional[Message] 
    if msg.reply_to_message:
       to_translate_text = msg.reply_to_message.text
       translator = Translator()
       try:
            translated = translator.translate(to_translate_text, dest="en")
            detect_text = (translator.detect(to_translate_text).confidence)
            sourcel = translated.src
            if detect_text>=1: 
                 detect_text="~Precisely" 
            else:
                 detect_text="~Wild guess"
            translated_text = translated.text
            msg.reply_text("*Translated from {} {}:*\n{}".format(sourcel, detect_text, translated_text),parse_mode=ParseMode.MARKDOWN)
       except Exception as e:
               msg.reply_text("dammit! Something went wrong.")
    else:
         msg.reply_text("No message found for translating.")

__help__ = """- /tr translate replied text for you.
You can translate words or phrases using this command as reply to a long message. 
"""
__mod_name__ = "Translator"
