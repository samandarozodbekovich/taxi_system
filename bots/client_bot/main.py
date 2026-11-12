import asyncio
import logging

from handlers import router
from loader import bot, dp


async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
