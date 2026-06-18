import asyncio
import logging
from loader import bot, dp
from handlers import start

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Routerni ulash
    dp.include_router(start.router)
    
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")