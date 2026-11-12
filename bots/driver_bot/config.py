import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("DRIVER_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
WEBAPP_URL = os.getenv("DRIVER_WEBAPP_URL")
# FSM storage (driver login tokens) - survives bot restarts. Redis DB 3 is free (Channels 0, Celery 1, cache 2)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/3")
