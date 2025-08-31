from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.register import UserStates
from config import conf


async def send_first_name(message: Message, state: FSMContext) -> None:
    await message.answer("Ro'yhatdan o'tish")
    await message.answer("✍️ <b>Ismingizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.first_name)
