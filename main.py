from pymongo import MongoClient
import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from pprint import pprint

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

client = MongoClient('mongodb+srv://<username>:<password>@cluster0.mydh0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.admin
serverStatusResult = db.command("serverStatus")
pprint(serverStatusResult)