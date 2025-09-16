import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, BotCommandScopeChat, Message, Update

from bot.handlers import command_router, main_router, register_router, user_router, admin_routers, driver_routers
from bot.keyboard import UserButtons
from bot.middlewares import RegistrationMiddleware
from bot.utils.services import load_car_type_names
from config import conf
from database import Driver

dp = Dispatcher()


@main_router.message(F.text == UserButtons.BACK)
async def back_to_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    # /start komandasi kabi yangi Update yasash
    fake_message = message.model_copy(update={"text": "/start"})
    fake_update = Update(update_id=0, message=fake_message)

    # dispatcher orqali qayta ishlash
    await dp.feed_update(bot=message.bot, update=fake_update)


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
    await bot.delete_my_commands()


async def main_polling():
    dp.startup.register(on_start)
    dp.update.middleware(RegistrationMiddleware())
    dp.shutdown.register(on_shutdown)
    dp.include_routers(
        command_router,
        main_router,
        register_router,
        user_router,
        driver_routers,
        admin_routers
    )
    await load_car_type_names()
    bot = Bot(conf.bot.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_polling())
