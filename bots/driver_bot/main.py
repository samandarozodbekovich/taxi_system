import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import auth, menu

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(auth.router)
    dp.include_router(menu.router)

    logger.info("Driver bot ishga tushdi...")

    await bot.delete_webhook(drop_pending_updates=True)

    # ← Internet uzilsa avtomatik qayta ulanadi
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Polling xato: {e}")
            logger.info("5 soniyadan keyin qayta ulanadi...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")