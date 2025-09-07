from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.keyboard.reply import UserButtons, driver_info_keyboard_btn
from database import User, Driver
from utils.services import greeting_user

command_router = Router()


# @command_router.message(IsDriver(), CommandStart(), StateFilter(None))
# async def d_command_start_handler(message: Message, state: FSMContext) -> None:
#     await message.answer('Salom', reply_markup=driver_keyboard_btn().as_markup(resize_keyboard=True))
#     await state.clear()


@command_router.message(CommandStart(), StateFilter(None))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await greeting_user(message)
    await state.clear()


@command_router.message(Command(commands='myinfo'), StateFilter(None))
async def myinfo_command_handler(message: Message) -> None:
    rkb = ReplyKeyboardBuilder(
        [[KeyboardButton(text=UserButtons.CHANGE_FIRST_NAME), KeyboardButton(text=UserButtons.CHANGE_LAST_NAME)],
         [KeyboardButton(text=UserButtons.BACK), KeyboardButton(text=UserButtons.BECOME_DRIVER)], ])
    user = await User.get(message.from_user.id)
    user_photo = "https://cdn-icons-png.flaticon.com/512/1933/1933233.png"
    msg = f'''🙎🏻‍♂️ Ism: {user.first_name}
🙎🏻‍♂️ Familiya: {user.last_name}
📞 Telefon raqam: +998{user.phone_number}'''

    if driver := await Driver.filter(Driver.user_id == message.from_user.id):
        rkb = driver_info_keyboard_btn()
        driver = driver[0]
        user_photo = driver.image
        msg += F"""\n🏎 Mashina rusumi: {driver.car_brand}
🔢 Mashina raqami: <b><tg-spoiler>{driver.car_number}</tg-spoiler></b>"""
        if driver.has_permission:
            msg += f"Mashina toifasi {driver.car_type}"

    # 📊 Buyurtmalar soni: {await TestAnswer.count_by(TestAnswer.user_id == user.id)} ta
    await message.answer_photo(user_photo, caption=msg + "\nTanlang: 👇",
                               reply_markup=rkb.as_markup(resize_keyboard=True))

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
