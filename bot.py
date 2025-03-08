# TODO:
# connect to marketcoincap api DONE
# show crypto price from slug DONE
# make object instead of json for data DONE
# logging DONE
# Calculate RSI DONE
# when starting bot show all price changes then just latest prices DONE
# add a way to add more coin DONE
# show overbought/oversold
# Better interface DONE ?

# add auth to the bot
# command logging DONE
# make it accept obj not argument for job get request DONE
# Remove obj

import json

import os 
import datetime
import logging

from dotenv import load_dotenv
from functools import wraps
from request import requestPrice, requestUsage
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# loading env
load_dotenv()

channelKey = os.getenv("CHANNEL_KEY")
botKey = os.getenv("BOT_KEY")
# CLI logging
logging.basicConfig(
  format =' %(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level = logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

application = ApplicationBuilder().token(botKey).build()
job_queue = application.job_queue

class CoinInfo:
  objs = {}
  def __init__(self, coinMarketCapId: int, name: str, slug: str, price: float, volume24h: float, 
              volumeChange24h: float, percentChange1h: float, percentChange24h: float, 
              percentChange7d: float, percentChange30d: float, marketCap: float, marketCapDominance: float, 
              fullyDilutedMarketCap: float, lastUpdated: str):
    self.coinMarketCapId = coinMarketCapId
    self.name = name
    self.slug = slug
    self.price = [price]
    self.volume24h = volume24h
    self.volumeChange24h = volumeChange24h
    self.percentChange1h = percentChange1h
    self.percentChange24h = percentChange24h
    self.percentChange7d = percentChange7d
    self.percentChange30d = percentChange30d
    self.marketCap = marketCap
    self.marketCapDominance = marketCapDominance
    self.fullyDilutedMarketCap = fullyDilutedMarketCap
    self.lastUpdated = lastUpdated
    self.gain = []
    self.loss= []
    CoinInfo.objs[self.slug] = self
  
  def addCoinPrice(self, price:float):
    self.price.append(price)
    self.price = self.price[-14:]
    self.calculateGainLoss()

  def calculateGainLoss(self):
    if len(self.price) < 2:
        return

    prevPrice, currPrice = self.price[-2], self.price[-1]
    if prevPrice > currPrice: 
        self.gain.append(0.0)
        self.loss.append(prevPrice - currPrice)
    elif prevPrice < currPrice:
        self.gain.append(currPrice - prevPrice)
        self.loss.append(0.0)

    self.gain = self.gain[-14:]
    self.loss = self.loss[-14:]

  @classmethod
  def getAllObjs(cls) -> dict:
    return cls.objs

adminList = [os.getenv("ADMIN_LIST")]

# Functions
def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in adminList:
            print(f"Unauthorized access denied for {user_id}.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def errorCheck(res: dict|str):
  if type(res) == str:
    return True
    
# Logging Function
def commandLogging(command: str, user_data: list):
  logDir = os.path.join(os.path.dirname(__file__), "commandLogging")
  # make dir if it doesnt exist
  os.makedirs(logDir, exist_ok=True)
  logFilename = os.path.join(logDir, f"{datetime.datetime.now(datetime.UTC).date()}.txt")
  timestamp = datetime.datetime.now(datetime.UTC).time()
  with open(logFilename, "a") as file:
    file.write(f"{user_data[0]} - {user_data[1]} - {command} - {timestamp}\n")

def dataToObj(data: dict):
  for coin in data["data"].values(): 
    coin["name"] = CoinInfo(
      coinMarketCapId= coin["id"],
      name = coin["name"],
      slug = coin["slug"],
      price = coin["quote"]["USD"]["price"],
      volume24h = coin["quote"]["USD"]["volume_24h"],
      volumeChange24h = coin["quote"]["USD"]["volume_change_24h"],
      percentChange1h = coin["quote"]["USD"]["percent_change_1h"],
      percentChange24h = coin["quote"]["USD"]["percent_change_24h"],
      percentChange7d = coin["quote"]["USD"]["percent_change_7d"],
      percentChange30d = coin["quote"]["USD"]["percent_change_30d"],
      marketCap = coin["quote"]["USD"]["market_cap"],
      marketCapDominance = coin["quote"]["USD"]["market_cap_dominance"],
      fullyDilutedMarketCap = coin["quote"]["USD"]["fully_diluted_market_cap"],
      lastUpdated = coin["quote"]["USD"]["last_updated"]
    )

async def calculateRsiCallback(context: ContextTypes.DEFAULT_TYPE):
  coinData = requestPrice(slug = ",".join(CoinInfo.getAllObjs()).lower())
  if errorCheck(coinData):
    await context.bot.send_message(
      chat_id=context.job.chat_id, 
      text=f"Error: {coinData}")
    
    await context.bot.send_message(
      chat_id=channelKey, text="An error has occurred", 
      disable_notification=True)
    
    context.job_queue.get_jobs_by_name("run")[0].schedule_removal()

  for key, value in CoinInfo.getAllObjs().items():
    value.addCoinPrice(coinData["data"][str(value.coinMarketCapId)]["quote"]["USD"]["price"])
  
  text = ""
  rsiAlarm = ""
  for key, value in CoinInfo.getAllObjs().items():
    # its just average
    try:
      avg_gain = sum(value.gain) / len(value.gain)
      avg_loss = sum(value.loss) / len(value.loss)
        
      if avg_loss == 0:  
        rsi = 100  # No losses → RSI = 100 (overbought)
      elif avg_gain == 0:  
        rsi = 0    # No gains → RSI = 0 (oversold)
      else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    except ZeroDivisionError:
      rsi = 50  # Edge case (should never really happen)
    if (rsi >= 70 or rsi <= 30) and len(value.price) >= 14:
      rsiAlarm += f"{value.name} RSI: {round(rsi, 0)}\nCurrent Price: {value.price[-1]}\n"

    text += f"{value.name} RSI: {round(rsi, 0)}\nCurrent Price: {value.price[-1]} {len(value.price)}\n\n"

  if len(rsiAlarm) > 0:
    for x in range(3):
      await context.bot.send_message(
        chat_id=channelKey, 
        text=f"{rsiAlarm}", 
      )
   
  await context.bot.send_message(
    chat_id=channelKey, 
    text=f"{text}", 
    disable_notification=True)

# Commands
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):  
  chat_id = update.effective_chat.id
  # username = update.effective_chat.username
  first_name = update.effective_chat.first_name
  # last_name = update.effective_chat.last_name
  # context.user_data[chat_id] = [chat_id,first_name]
  
  commandLogging("Start", [chat_id, first_name])
  await context.bot.send_message(
    chat_id = chat_id,
    text=f"Welcome {first_name}\nCheck API Usage: /check\nRun program: /run (coin name),(coin name)...\nExample: /run bitcoin,dogecoin"
    )

@restricted
async def checkUsage(update: Update, context: ContextTypes.DEFAULT_TYPE):
  credits_used, credits_left, credit_limit_monthly_reset_timestamp = requestUsage().values()
  await context.bot.send_message(
    chat_id = update.effective_chat.id,
  	text = f"credits_used: {credits_used} \ncredits_left: {credits_left} \nreset_timestamp: {credit_limit_monthly_reset_timestamp}"
  )

@restricted
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  username = update.effective_chat.username

  if context.job_queue.get_jobs_by_name("run"):
    await context.bot.send_message(
      chat_id = chat_id,
      text = "Bot already running to stop use /stop"
    )
    return

  commandLogging(f"Run {context.args}", [chat_id, username])
  #check if theres any coin
  if not CoinInfo.getAllObjs() == None and not context.args:
    await context.bot.send_message(
      chat_id = chat_id,
      text = "Add coin to argument\nExample: /run Dogecoin Bitcoin"
    )
    return
  
  args = ",".join(context.args).lower()
  res = requestPrice(slug = args)
  if errorCheck(res): 
    await context.bot.send_message(chat_id=chat_id, text=f"Error: {res}")
    return
  else:
    dataToObj(res)
    context.job_queue.run_repeating(calculateRsiCallback, 300, chat_id=chat_id, name = "run")

    txt = f"Running RSI for: {context.args}\n\n"
    for key, value in CoinInfo.getAllObjs().items():
      txt += f"{value.name}\n"
      txt += f"Opening price: {value.price[-1]}\n"
      txt += f"Volume 24H: {value.volume24h}\n"
      txt += f"Volume Change 24H: {value.volumeChange24h}\n"
      txt += f"Percent Change 1H: {value.percentChange1h}\n"
      txt += f"Percent Change 24H: {value.percentChange24h}\n"
      txt += f"Percent Change 7D: {value.percentChange7d}\n"
      txt += f"Percent Change 30D: {value.percentChange30d}\n"
      txt += f"Last Updated: {value.lastUpdated}\n\n"

    await context.bot.send_message(
      chat_id = channelKey,
      text = txt,
      disable_notification=True
    )

@restricted
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.job_queue.get_jobs_by_name("run"):
    chat_id = update.effective_chat.id
    username = update.effective_chat.username
    commandLogging(f"Stop", [chat_id, username])
    await context.bot.send_message(
      chat_id = chat_id,
      text = "Stopping bot"
    )
  else:
    await context.bot.send_message(
    chat_id = chat_id,
    text = "No Job found"
    )
    
@restricted
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  username = update.effective_chat.username
  commandLogging(f"add {context.args}", [chat_id, username])

  args = ",".join(context.args).lower()
  res = requestPrice(slug = args)

  if errorCheck(res): 
    await context.bot.send_message(chat_id=chat_id, text=f"Error: {res}")
    return
  else:
    dataToObj(requestPrice(slug = context.args))
    txt = f"Adding coin RSI for: {context.args}\n\n"
    for key, value in CoinInfo.getAllObjs().items():
      txt += f"{value.name}\n"
      txt += f"Opening price: {value.price[-1]}\n"
      txt += f"Volume 24H: {value.volume24h}\n"
      txt += f"Volume Change 24H: {value.volumeChange24h}\n"
      txt += f"Percent Change 1H: {value.percentChange1h}\n"
      txt += f"Percent Change 24H: {value.percentChange24h}\n"
      txt += f"Percent Change 7D: {value.percentChange7d}\n"
      txt += f"Percent Change 30D: {value.percentChange30d}\n"
      txt += f"Last Updated: {value.lastUpdated}\n\n"

    await context.bot.send_message(
      chat_id = channelKey,
      text = txt,
      disable_notification=True
    )

    await context.bot.send_message(
      chat_id = chat_id,
      text = f"Coin added: {context.args}"
    )

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('checkApi', checkUsage))
application.add_handler(CommandHandler('run', run))
application.add_handler(CommandHandler('add', add))
application.add_handler(CommandHandler('stop', stop))


if __name__ == '__main__':
  # runs the bot until you hit CTRL+C
  application.run_polling()
