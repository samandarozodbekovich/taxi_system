import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("DRIVER_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
WEBAPP_URL = os.getenv("DRIVER_WEBAPP_URL")


