from aiogram import Router, Bot, F
from aiogram.types import Message

from bot.keyboard.reply import UserButtons
from config import conf

main_router = Router()


@main_router.message(F.text == UserButtons.OPERATOR)
async def show_operator_handler(message: Message):
    await message.answer(
        f'👨‍💼 Admin {conf.bot.OPERATOR_NUMBER}')


