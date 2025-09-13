from typing import Callable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboard import main_keyboard_btn
from bot.states.user import UserStates
from database import Driver
from database.models import CarType

CAR_TYPE_NAMES = []


async def get_car_type_names():
    """Get all car type IDs from database"""
    car_types = await CarType.all()
    return [ct.name for ct in car_types]


async def load_car_type_names():
    """Load car type IDs into global variable"""
    global CAR_TYPE_NAMES
    CAR_TYPE_NAMES = await get_car_type_names()


async def greeting_user(message: Message):
    is_driver: bool = bool(await Driver.filter((Driver.user_id == message.from_user.id) & (Driver.has_permission)))
    await message.answer(
        f"<b>👋 Assalomu alaykum <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>, botimizga xush kelibsiz.</b>",
        reply_markup=main_keyboard_btn(is_driver=is_driver).as_markup(resize_keyboard=True))


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


def driver_info_msg(driver: Driver) -> str:
    msg = f'''🙎🏻‍♂️ Ism: {driver.user.first_name}
🙎🏻‍♂️ Familiya: {driver.user.last_name}
📞 Telefon raqam: +998{driver.user.phone_number}
🏎 Mashina rusumi: {driver.car_brand}
🔢 Mashina raqami: <b><tg-spoiler>{driver.car_number}</tg-spoiler></b>
Mashina toifasi: <b><i><u> {driver.car_type.name} </u></i></b>'''
    if driver.has_permission:
        msg += f"\n<b>Hurmatli user sizda taxistlik huquqi bor</b>"
    else:
        msg += f"\n<b><strike>Sizda hozircha taxistlik huquqi yoq</strike></b>"
    return msg
