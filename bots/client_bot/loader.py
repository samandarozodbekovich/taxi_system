import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")
# Must match BOT_API_SECRET in the backend
BOT_API_SECRET = os.getenv("BOT_API_SECRET", "")
# The backend recognizes bot requests by this header
API_HEADERS = {"X-Bot-Secret": BOT_API_SECRET}
# Client Mini App (ordering a taxi on the map)
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
