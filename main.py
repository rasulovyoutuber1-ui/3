import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import config, logger
from middlewares.check_sub import CheckSubscriptionMiddleware
from handlers.user import user_router
from handlers.owner import owner_router
from database import init_db

async def main():
    logger.info("Baza ishga tushirilmoqda...")
    await init_db()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.outer_middleware(CheckSubscriptionMiddleware())
    dp.callback_query.outer_middleware(CheckSubscriptionMiddleware())

    dp.include_router(owner_router)
    dp.include_router(user_router)

    logger.info("🚀 Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
