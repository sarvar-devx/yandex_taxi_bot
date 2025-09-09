import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.handlers.admin import admin_router
from bot.handlers.commands import command_router
from bot.handlers.driver import driver_router
from bot.handlers.driver_info import driver_info_router
from bot.handlers.main import main_router
from bot.handlers.register import register_router
from bot.handlers.user import user_router
from bot.middlewares import RegistrationMiddleware
from config import conf
from database import Driver


async def on_start(bot: Bot):
    user_commands = [
        BotCommand(command='start', description="🏁 Bo'tni ishga tushirish"),
        BotCommand(command='myinfo', description="📝 Mening malumotlarim"),
        BotCommand(command='help', description="🆘 yordam"),
    ]
    await bot.set_my_commands(commands=user_commands)
    driver_commands = user_commands + [BotCommand(command="delete_driver_profile",
                                                  description="Taxist profilni o'chirib yuborish")]
    drivers = await Driver.all()
    for driver in drivers:
        await bot.set_my_commands(driver_commands, BotCommandScopeChat(chat_id=driver.user_id))


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    pass
    # await bot.delete_my_commands()


async def main_polling():
    dp = Dispatcher()
    dp.startup.register(on_start)
    dp.update.middleware(RegistrationMiddleware())
    dp.shutdown.register(on_shutdown)
    dp.include_routers(
        command_router,
        main_router,
        register_router,
        user_router,
        driver_router,
        admin_router,
        driver_info_router
    )
    bot = Bot(conf.bot.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_polling())
