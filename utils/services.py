from typing import Callable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboard.reply import main_keyboard_btn
from bot.states.user import UserStates
from database import Driver


async def greeting_user(message: Message):
    driver_exists: bool = bool(await Driver.get(user_id=message.from_user.id))
    await message.answer(
        f"<b>👋 Assalomu alaykum <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>, botimizga xush kelibsiz.</b>",
        reply_markup=main_keyboard_btn(is_driver=driver_exists).as_markup(resize_keyboard=True))


async def wrong_first_last_name(message: Message) -> None:
    await message.answer('<b>🙅 Ism yoki Familiyada faqat harflardan iboorat</b>')


async def send_first_name(message: Message, state: FSMContext) -> None:
    await message.answer("Ro'yhatdan o'tish")
    await message.answer("✍️ <b>Ismingizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.first_name)


async def send_last_name(message: Message, state: FSMContext) -> None:
    await message.answer('✍ <b>Familiyangizni kiriting.</b>')
    await state.set_state(UserStates.last_name)


async def validate_name_input(message: Message, retry_function: Callable, state: FSMContext = None) -> bool:
    if not message.text or not message.text.isalpha():
        await wrong_first_last_name(message)
        await retry_function(message, state)
        return False
    return True
