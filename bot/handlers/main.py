from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.commands import command_start_handler
from bot.keyboard.reply import UserButtons
from config import conf

main_router = Router()

@main_router.message(F.text == UserButtons.BACK)
async def back_admin_menu_handler(message: Message, state: FSMContext):
    await command_start_handler(message, state)


@main_router.message(F.text == UserButtons.OPERATOR,  StateFilter(None))
async def show_operator_handler(message: Message):
    await message.answer(
        f'👨‍💼 Admin {conf.bot.OPERATOR_NUMBER}')
