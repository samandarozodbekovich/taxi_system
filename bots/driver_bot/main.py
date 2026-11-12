import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config import BOT_TOKEN, REDIS_URL
from handlers import auth, menu

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    # Redis keeps drivers logged in across bot restarts (MemoryStorage lost every session)
    dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))

    dp.include_router(auth.router)
    dp.include_router(menu.router)

    logger.info("Driver bot started...")

    await bot.delete_webhook(drop_pending_updates=True)

    # Reconnects automatically if the connection drops
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            logger.info("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")