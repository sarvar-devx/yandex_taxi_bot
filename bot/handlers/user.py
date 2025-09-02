from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.handlers.commands import myinfo_command_handler
from bot.keyboard.reply import UserButtons
from bot.states.user import ChangeNameStates
from db import User
from utils.services import validate_name_input

user_router = Router()


@user_router.message(F.text == UserButtons.CHANGE_FIRST_NAME)
async def send_first_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Ismingizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.first_name)


@user_router.message(ChangeNameStates.first_name)
async def change_first_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_first_name_handler, state):
        return

    await User.update(message.from_user.id, first_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning ismingiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()


@user_router.message(F.text == UserButtons.CHANGE_LAST_NAME)
async def send_last_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Familiyangizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.last_name)


@user_router.message(ChangeNameStates.last_name)
async def change_last_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_last_name_handler, state):
        return

    await User.update(message.from_user.id, last_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning familiyangiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()
