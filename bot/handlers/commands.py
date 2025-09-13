from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.filters.checker import DriverHasPermission, IsDriver, IsAdmin
from bot.keyboard import DriverInfoInlineKeyboardButtons, UserButtons, driver_keyboard_btn, DriverButtons, \
    admin_keyboard_btn
from database import User, Driver
from utils.services import greeting_user, driver_info_msg

command_router = Router()


@command_router.message(DriverHasPermission(), CommandStart(), StateFilter(None))
async def d_command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Salom', reply_markup=driver_keyboard_btn().as_markup(resize_keyboard=True))
    await state.clear()


@command_router.message(IsDriver(), Command(commands='delete_driver_profile'), StateFilter(None))
async def delete_driver_command_handler(message: Message) -> None:
    await message.answer("Haqiqatdan ham taxist bolib ishlashdan bosh tortasizmi", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Ha men haqiqatdan roziman", callback_data=f"reject_driving"),
                          InlineKeyboardButton(text="Yoq men adashdim", callback_data="cancel")]]))


@command_router.message(IsAdmin(), CommandStart(), StateFilter(None))
async def admin_command_start_handler(message: Message) -> None:
    await message.answer('Salom', reply_markup=admin_keyboard_btn().as_markup(resize_keyboard=True))


@command_router.message(CommandStart(), StateFilter(None))
async def command_start_handler(message: Message) -> None:
    await greeting_user(message)


@command_router.message(Command(commands='myinfo'), StateFilter(None))
async def myinfo_command_handler(message: Message) -> None:
    rkb = ReplyKeyboardBuilder(
        [[KeyboardButton(text=UserButtons.CHANGE_FIRST_NAME), KeyboardButton(text=UserButtons.CHANGE_LAST_NAME)],
         [KeyboardButton(text=UserButtons.BACK)]])
    user = await User.get(message.from_user.id)
    msg = f'''🙎🏻‍♂️ Ism: {user.first_name}
🙎🏻‍♂️ Familiya: {user.last_name}
📞 Telefon raqam: +998{user.phone_number}'''

    if driver := await Driver.get(user_id=message.from_user.id, relationship=Driver.car_type):
        ikb = DriverInfoInlineKeyboardButtons.get_markup()
        msg = driver_info_msg(driver)
        await message.answer_photo(driver.image, caption=msg + "\nTanlang: 👇", reply_markup=ikb)
        await message.answer("Tanlang", reply_markup=rkb.as_markup(resize_keyboard=True))
        return
    rkb.row(KeyboardButton(text=UserButtons.BECOME_DRIVER))
    await message.answer_photo("https://cdn-icons-png.flaticon.com/512/1933/1933233.png", caption=msg + "\nTanlang: 👇",
                               reply_markup=rkb.as_markup(resize_keyboard=True))

    # 📊 Buyurtmalar soni: {await TestAnswer.count_by(TestAnswer.user_id == user.id)} ta


@command_router.message(Command(commands='help'), StateFilter(None))
async def help_command_handler(message: Message) -> None:
    await message.answer(F'''Buyruqlar:
/delete_driver_profile - Botdan o'z ma'lumotlaringgizi toliq yo'q qilish \n
/start - Siz bu buyruq bilan botni ishga tushirasiz \n
/myinfo - Uzingizning malumotlaringizni yangilaysiz \n
/help - Botning vazifalarini tushinish\n
Tugmalar:
<i>{UserButtons.ORDER_TAXI}</i> - O'zinggizga taksi buyurtma qilish \n
<i>{UserButtons.OPERATOR}</i> - Admin bilan bog'lanish \n
<i>{UserButtons.CHANGE_FIRST_NAME}</i> - Botda o'z ismingizni ozgartirish\n
<i>{UserButtons.CHANGE_LAST_NAME}</i> - Botda o'z familiyangizni ozgartirish\n
<i>{UserButtons.BECOME_DRIVER}</i> - Haydovchi taksist sifatda ishlash\n
<i>{UserButtons.ORDER_HISTORY}</i> - Buyurtmalar tarixini korish\n
<i>{DriverButtons.GO}</i> - Botdan foyalanishni boshlash\n
<i>{DriverButtons.START_WORK}</i> - Taksist sifatida ishni boshlash\n
<i>{DriverButtons.FINISH_WORK}</i> - Taksist sifatida ishni tugatish\n
<i>Agar sizda qandaydir muammo bulsa yoki savollaringiz bulsa <a href='https://t.me/Bewrlius_py'>Operatorga</a> ga murojat qiling</i>
''')
