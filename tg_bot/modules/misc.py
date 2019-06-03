import subprocess
import html
import json
import random
import time
import pyowm
import re
import wikipedia
from pyowm import timeutils, exceptions
from datetime import datetime
from typing import Optional, List
from pythonping import ping as ping3
from typing import Optional, List
from PyLyrics import *

import requests
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.error import BadRequest

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER
from tg_bot.__main__ import GDPR
from tg_bot.__main__ import STATS, USER_INFO
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.chat_status import is_user_admin, user_admin, can_restrict 
from tg_bot.modules.sql.translation import prev_locale

from tg_bot.modules.translations.strings import tld

from requests import get

GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"
GMAPS_TIME = "https://maps.googleapis.com/maps/api/timezone/json"


@run_async
def runs(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    update.effective_message.reply_text(random.choice(tld(chat.id, "RUNS-K")))


@run_async
def slap(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user

    temp = random.choice(tld(chat.id, "SLAP_TEMPLATES-K"))
    item = random.choice(tld(chat.id, "ITEMS-K"))
    hit = random.choice(tld(chat.id, "HIT-K"))
    throw = random.choice(tld(chat.id, "THROW-K"))
    itemp = random.choice(tld(chat.id, "ITEMP-K"))
    itemr = random.choice(tld(chat.id, "ITEMR-K"))

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw, itemp=itemp, itemr=itemr)
    #user1=user1, user2=user2, item=item_ru, hits=hit_ru, throws=throw_ru, itemp=itemp_ru, itemr=itemr_ru

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
def get_bot_ip(bot: Bot, update: Update):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@run_async
def get_id(bot: Bot, update: Update, args: List[str]):
    user_id = extract_user(update.effective_message, args)
    chat = update.effective_chat  # type: Optional[Chat]
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(tld(chat.id,
                "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.").format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = bot.get_chat(user_id)
            update.effective_message.reply_text(tld(chat.id, "{}'s id is `{}`.").format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text(tld(chat.id, "Your id is `{}`.").format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text(tld(chat.id, "This group's id is `{}`.").format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)


@run_async
def info(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)
    chat = update.effective_chat  # type: Optional[Chat]
    
    if user_id:
        user = bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text(tld(chat.id, "I can't extract a user from this."))
        return

    else:
        return

    text =  tld(chat.id, "<b>User info</b>:")
    text += "\nID: <code>{}</code>".format(user.id)
    text += tld(chat.id, "\nFirst Name: {}").format(html.escape(user.first_name))

    if user.last_name:
        text += tld(chat.id, "\nLast Name: {}").format(html.escape(user.last_name))

    if user.username:
        text += tld(chat.id, "\nUsername: @{}").format(html.escape(user.username))

    text += tld(chat.id, "\nPermanent user link: {}").format(mention_html(user.id, "link"))

    if user.id == OWNER_ID:
        text += tld(chat.id, "\n\nThis person is my owner - I would never do anything against them!")
    else:
        if user.id in SUDO_USERS:
            text += tld(chat.id, "\nThis person is one of my sudo users! " \
            "Nearly as powerful as my owner - so watch it.")
        else:
            if user.id in SUPPORT_USERS:
                text += tld(chat.id, "\nThis person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map.")

            if user.id in WHITELIST_USERS:
                text += tld(chat.id, "\nThis person has been whitelisted! " \
                        "That means I'm not allowed to ban/kick them.")

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id, chat.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def get_time(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat  # type: Optional[Chat]
    location = " ".join(args)
    if location.lower() == bot.first_name.lower():
        update.effective_message.reply_text(tld(chat.id, "Its always banhammer time for me!"))
        bot.send_sticker(chat.id, BAN_STICKER)
        return

    res = requests.get(GMAPS_LOC, params=dict(address=location, key=MAPS_API))

    if res.status_code == 200:
        loc = json.loads(res.text)
        print(loc)
        if loc.get('status') == 'OK':
            lat = loc['results'][0]['geometry']['location']['lat']
            long = loc['results'][0]['geometry']['location']['lng']

            country = None
            city = None

            address_parts = loc['results'][0]['address_components']
            for part in address_parts:
                if 'country' in part['types']:
                    country = part.get('long_name')
                if 'administrative_area_level_1' in part['types'] and not city:
                    city = part.get('long_name')
                if 'locality' in part['types']:
                    city = part.get('long_name')

            if city and country:
                location = "{}, {}".format(city, country)
            elif country:
                location = country

            timenow = int(datetime.utcnow().timestamp())
            res = requests.get(GMAPS_TIME, params=dict(location="{},{}".format(lat, long), timestamp=timenow, key=MAPS_API))

            if res.status_code == 200:
                offset = json.loads(res.text)['dstOffset']
                timestamp = json.loads(res.text)['rawOffset']
                time_there = datetime.fromtimestamp(timenow + timestamp + offset).strftime("%H:%M:%S on %A %d %B")
                update.message.reply_text(tld(chat.id, "It's {} in {}").format(time_there, location))


@run_async 
@user_admin
def echo(bot: Bot, update: Update):
    message = update.effective_message
    message.delete()
    args = update.effective_message.text.split(None, 1)
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)

@run_async
def stickerid(bot: Bot, update: Update):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text("Sticker ID:\n```" + 
                                            escape_markdown(msg.reply_to_message.sticker.file_id) + "```",
                                            parse_mode=ParseMode.MARKDOWN)
    else:
        update.effective_message.reply_text(tld(update.effective_chat, "Please reply to a sticker to get its ID."))


@run_async
def getsticker(bot: Bot, update: Update):
    msg = update.effective_message
    chat_id = update.effective_chat.id 
    if msg.reply_to_message:
       if msg.reply_to_message and msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id 
            newFile = bot.get_file(file_id)
            newFile.download('sticker.png')
            bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
            os.remove("sticker.png")
       elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
            newFile = bot.get_file(file_id)
            newFile.download('sticker.png')
            bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
            os.remove("sticker.png")
       elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
            newFile = bot.get_file(file_id)
            newFile.download('sticker.png')
            bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
            os.remove("sticker.png") 
       else:
           update.effective_message.reply_text(tld(chat_id, "Unknown format sticker/photo/document are the supported formats."))
    else:
        update.effective_message.reply_text(tld(chat_id, "Please reply to a sticker/photo/document for me to upload its PNG."))


@run_async
def gdpr(bot: Bot, update: Update):
    update.effective_message.reply_text(tld(update.effective_chat.id, "Deleting identifiable data...Please wait!"))
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text("Your personal data has been deleted.\n\nNote that this will not unban "
                                        "you from any chats, as that is telegram data, not Marie data. "
                                        "Flooding, warns, and gbans are also preserved, as of "
                                        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/), "
                                        "which clearly states that the right to erasure does not apply "
                                        "\"for the performance of a task carried out in the public interest\", as is "
                                        "the case for the aforementioned pieces of data.",
                                        parse_mode=ParseMode.MARKDOWN)

@run_async
def markdown_help(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    update.effective_message.reply_text(tld(chat.id, "MARKDOWN_HELP-K"), parse_mode=ParseMode.HTML)
    #update.effective_message.reply_text(tld(chat.id, "Try forwarding the following message to me, and you'll see!"))
    #update.effective_message.reply_text(tld(chat.id, "/save test This is a markdown test. _italics_, *bold*, `code`, "
    #                                    "[URL](example.com) [button](buttonurl:github.com) "
    #                                    "[button2](buttonurl://google.com:same)"))


@run_async
def stats(bot: Bot, update: Update):
    update.effective_message.reply_text("Current stats:\n" + "\n".join([mod.__stats__() for mod in STATS]))


@run_async 
@user_admin
def ping(bot: Bot, update: Update): 
    start_time = time.time()
    requests.get('http://api.telegram.org')
    end_time = time.time()
    ping_time = float(end_time - start_time)*1000
    update.effective_message.reply_text("Pong!, speed was : `{}`ms".format(ping_time),parse_mode=ParseMode.MARKDOWN)


@run_async
def reply_keyboard_remove(bot: Bot, update: Update):
    reply_markup = ReplyKeyboardRemove()
    old_message = bot.send_message(
        chat_id=update.message.chat_id,
        text='trying',
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id
    )
    bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=old_message.message_id
    )


LYRICSINFO = "\n[Full Lyrics](http://lyrics.wikia.com/wiki/%s:%s)"

@run_async
def lyrics(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    text = message.text[len('/lyrics '):]
    song = " ".join(args).split("- ")
    reply_text = f'Looks up for lyrics'
    
    if len(song) == 2:
        while song[1].startswith(" "):
            song[1] = song[1][1:]
        while song[0].startswith(" "):
            song[0] = song[0][1:]
        while song[1].endswith(" "):
            song[1] = song[1][:-1]
        while song[0].endswith(" "):
            song[0] = song[0][:-1]
        try:
            lyrics = "\n".join(PyLyrics.getLyrics(
                song[0], song[1]).split("\n")[:20])
        except ValueError as e:
            return update.effective_message.reply_text("Song %s not found :(" % song[1], failed=True)
        else:
            lyricstext = LYRICSINFO % (song[0].replace(
                " ", "_"), song[1].replace(" ", "_"))
            return update.effective_message.reply_text(lyrics + lyricstext, parse_mode="MARKDOWN")
    else:
        return update.effective_message.reply_text("Invalid syntax- try Artist - Title!", failed=True)


@run_async
def ud(bot: Bot, update: Update):
  message = update.effective_message
  text = message.text[len('/ud '):]
  results = get(f'http://api.urbandictionary.com/v0/define?term={text}').json()
  reply_text = f'Word: {text}\nDefinition: {results["list"][0]["definition"]}'
  message.reply_text(reply_text)


def wiki(bot: Bot, update: Update):
        query = str(update.effective_message.text[6:])
        result = '**Search:**\n' + query + '\n\n**Result:**\n' + str(wikipedia.summary(query))
        update.effective_message.reply_markdown(result)


def google(bot: Bot, update: Update):
  query = update.effective_message.text.split(None, 1)
  result_ = subprocess.run(['gsearch', str(query)], stdout=subprocess.PIPE)
  result = str(result_.stdout.decode())
  update.effective_message.reply_markdown('*Searching:*\n`' + str(query) + '`\n\n*RESULTS:*\n' + result)


@run_async
def insults(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    text = random.choice(tld(chat.id, "INSULTS-K"))
    update.effective_message.reply_text(text)


# /ip is for private use
__help__ = """
 - /id: get the current group id. If used by replying to a message, gets that user's id.
 - /runs: reply a random string from an array of replies.
 - /insults: reply a random string from an array of replies.
 - /slap: slap a user, or get slapped if not a reply.
 - /info: get information about a user.
 - /gdpr: deletes your information from the bot's database. Private chats only.
 - /stickerid: reply to a sticker to me to tell you its file ID.
 - /getsticker: reply to a sticker to me to upload its raw PNG file.
 - /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats.
 - /lyrics: Find your favorite songs lyrics!
 - /ud: Type the word or expression you want to search. For example /ud Gay
 - /wiki: Query the Wikipedia
 - /removebotkeyboard: Got a nasty bot keyboard stuck in your group?
 - /google: Google search
"""

__mod_name__ = "Misc"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True, admin_ok=True)
IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID), admin_ok=True)
PING_HANDLER = DisableAbleCommandHandler("ping", ping, admin_ok=True)
LYRICS_HANDLER = DisableAbleCommandHandler("lyrics", lyrics, pass_args=True, admin_ok=True)


INSULTS_HANDLER = DisableAbleCommandHandler("insults", insults, admin_ok=True)
RUNS_HANDLER = DisableAbleCommandHandler("runs", runs, admin_ok=True)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True, admin_ok=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True, admin_ok=True)

ECHO_HANDLER = CommandHandler("send", echo)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)

STATS_HANDLER = CommandHandler("stats", stats, filters=Filters.user(OWNER_ID))
GDPR_HANDLER = CommandHandler("gdpr", gdpr, filters=Filters.private)

UD_HANDLER = DisableAbleCommandHandler("ud", ud)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
GOOGLE_HANDLER = DisableAbleCommandHandler("google", google)


dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(INSULTS_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(PING_HANDLER)
#dispatcher.add_handler(GOOGLE_HANDLER)
dispatcher.add_handler(LYRICS_HANDLER)
dispatcher.add_handler(DisableAbleCommandHandler("removebotkeyboard", reply_keyboard_remove))
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(GOOGLE_HANDLER)
