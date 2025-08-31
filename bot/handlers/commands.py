from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import conf
from db import User

command_router = Router()


# @command_router.message(CommandStart())
# async def command_start_handler(message: Message, state: FSMContext) -> None:
#     await greeting_user(message)


@command_router.message(Command(commands='cancel'))
async def command_cancel_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Bekor qilindi')
    await state.clear()

# @command_router.message(Command(commands='myinfo'))
# async def myinfo_command_handler(message: Message) -> None:
#     rkb = ReplyKeyboardBuilder(
#         [[KeyboardButton(text=UserButtons.CHANGE_FIRST_NAME), KeyboardButton(text=UserButtons.CHANGE_LAST_NAME)],
#          [KeyboardButton(text=UserButtons.BACK)]])
#     user = await User.get(message.from_user.id)
#     await message.answer(f'''🙎🏻‍♂️ Ism: {user.first_name}
# 🙎🏻‍♂️ Familiya: {user.last_name}
# 📞 Telefon raqam: +998{user.phone_number}
# 📊 Qatnashgan testlar soni: {await TestAnswer.count_by(TestAnswer.user_id == user.id)} ta
# Tanlang: 👇''', reply_markup=rkb.as_markup(resize_keyboard=True))
#
#
# @command_router.message(Command(commands='help'))
# async def help_command_handler(message: Message) -> None:
#     await message.answer(F'''Buyruqlar:
# /start - Siz bu buyruq bilan botni ishga tushirasiz \n
# /myinfo - Uzingizning malumotlaringizni yangilaysiz \n
# /help - Botning vazifalarini tushinish\n
# Tugmalar:
# <i>{UserButtons.CHECK_ANSWER}</i> - Botga kiritilgan testlarni javoblarini kiritish\n
# <i>{UserButtons.ADMIN}</i> - Admin bilan bog'lanish \n
# <i>{UserButtons.REFERRAL_USER}</i> - Do'stlaringizni taklif qiling va bot sizga OLIMPIADA boʻladigan kanal uchun bir martalik link beradi\n
# <i>Agar sizda qandaydir muammo bulsa yoki savollaringiz bulsa <a href='https://t.me/Xumoyun_a'>Admin</a> ga murojat qiling</i>
# ''')
