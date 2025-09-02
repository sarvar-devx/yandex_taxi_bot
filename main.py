import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.handlers.commands import command_router
from bot.handlers.main import main_router
from bot.handlers.register import register_router
from bot.handlers.user import user_router
from bot.middlewares import RegistrationMiddleware
from config import conf


async def on_start(bot: Bot):
    user_commands = [
        BotCommand(command='start', description="🏁 Bo'tni ishga tushirish"),
        BotCommand(command='cancel', description="❌ Bekor qilish"),
        BotCommand(command='myinfo', description="📝 Mening malumotlarim"),
        BotCommand(command='help', description="🆘 yordam"),
    ]
    await bot.set_my_commands(commands=user_commands)


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_my_commands()


async def main_polling():
    dp = Dispatcher()
    dp.startup.register(on_start)
    dp.update.middleware(RegistrationMiddleware())
    dp.shutdown.register(on_shutdown)
    dp.include_routers(
        main_router,
        register_router,
        command_router,
        user_router
    )
    bot = Bot(conf.bot.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_polling())
