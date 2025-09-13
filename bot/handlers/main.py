from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.handlers.commands import myinfo_command_handler
from bot.keyboard import UserButtons
from bot.states.user import ChangeNameStates
from config import conf
from database import User
from utils.services import validate_name_input

main_router = Router()


@main_router.message(F.text == UserButtons.OPERATOR, StateFilter(None))
async def show_operator_handler(message: Message):
    await message.answer(
        f'👨‍💼 Admin {conf.bot.OPERATOR_NUMBER}')


@main_router.message(F.text == UserButtons.CHANGE_FIRST_NAME, StateFilter(None))
async def send_first_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Ismingizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.first_name)


@main_router.message(ChangeNameStates.first_name)
async def change_first_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_first_name_handler, state):
        return

    await User.update(message.from_user.id, first_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning ismingiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()


@main_router.message(F.text == UserButtons.CHANGE_LAST_NAME, StateFilter(None))
async def send_last_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Familiyangizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.last_name)


@main_router.message(ChangeNameStates.last_name)
async def change_last_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_last_name_handler, state):
        return

    await User.update(message.from_user.id, last_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning familiyangiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()
