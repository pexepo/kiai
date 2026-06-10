import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from kiai import db
from kiai.config import BOT_TOKEN
from kiai.handlers import router


async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    db.init()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    logging.getLogger(__name__).info('Kiai Render is up - long polling started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
