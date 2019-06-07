import random, re
from random import randint
from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler




TOSS = (
    "Heads",
    "Tails",
)

@run_async
def roll(bot: Bot, update: Update):
    update.message.reply_text(random.choice(range(1, 7)))
	
def toss(bot: Bot, update: Update):
    update.message.reply_text(random.choice(TOSS))

@run_async
def shrug(bot: Bot, update: Update):
  # reply to correct message
  reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
  reply_text("¯\_(ツ)_/¯")	
	
	
def decide(bot: Bot, update: Update):
      r = randint(1, 100)
      if r <= 65:
          update.message.reply_text("Yes.")
      elif r <= 90:
          update.message.reply_text("NoU.")
      else:
          update.message.reply_text("Maybe.")
            
def table(bot: Bot, update: Update):
          r = randint(1, 100)
          if r <= 45:
              update.message.reply_text("(╯°□°）╯彡 ┻━┻")
          elif r <= 90:
              update.message.reply_text("Send money to buy a new table to flip")
          else:
              update.message.reply_text("Go do some work instead of flippin tables you useless fellow.")
		

@run_async
def shout(bot: Bot, update: Update, args):
    msg = "```"
    text = " ".join(args)
    result = []
    result.append(' '.join([s for s in text]))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + ' ' + '  ' * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return update.effective_message.reply_text(msg, parse_mode="MARKDOWN")


__help__ = """
 - /shrug : get shrug XD.
 - /table : get flip/unflip :v.
 - /decide : Randomly answers yes/no/maybe
 - /toss : Tosses A coin
 - /roll : Roll a dice.
 - /shout <keyword>: write anything you want to give loud shout.
"""

__mod_name__ = "Extras"

ROLL_HANDLER = DisableAbleCommandHandler("roll", roll)
TOSS_HANDLER = DisableAbleCommandHandler("toss", toss)
SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)
TABLE_HANDLER = DisableAbleCommandHandler("table", table)
SHOUT_HANDLER = DisableAbleCommandHandler("shout", shout, pass_args=True)

dispatcher.add_handler(ROLL_HANDLER)
dispatcher.add_handler(TOSS_HANDLER)
dispatcher.add_handler(SHRUG_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(TABLE_HANDLER)
dispatcher.add_handler(SHOUT_HANDLER)
