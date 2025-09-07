import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.filters.checker import IsDriver
from bot.keyboard.reply import DriverButtons, driver_keyboard_btn, back_button_markup
from bot.states.user import DriverUpdateStates
from database import Driver

driver_router = Router()
driver_router.message.filter(IsDriver())
driver_router.callback_query.filter(IsDriver())


@driver_router.message(F.text == DriverButtons.CHANGE_CAR_BRAND, StateFilter(None))
async def update_car_brand_handler(message: Message, state: FSMContext):
    await message.answer("📝 Yangi model nomini kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.car_brand)


@driver_router.message(DriverUpdateStates.car_brand)
async def change_car_brand_handler(message: Message, state: FSMContext):
    if not message.text.split():
        await message.answer("‼️ Mashina brendi bosh bolishi mumkun emas qaytadan kiriting")
        await state.set_state(DriverUpdateStates.car_brand)
        return
    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, car_brand=message.text)
    await message.answer(f"✅ Mashina brandi {message.text.title()}ga ozgartirildi !")
    await state.clear()


@driver_router.message(IsDriver(), F.text == DriverButtons.CHANGE_CAR_NUMBER, StateFilter(None))
async def update_car_number_handler(message: Message, state: FSMContext):
    await message.answer("🔢  Yangi raqamni kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.car_number)


@driver_router.message(DriverUpdateStates.car_number)
async def change_car_number_handler(message: Message, state: FSMContext):
    pattern = r'^(01|10|20|25|30|40|50|60|70|75|80|85|90|95)\s[A-Z]{1}\s\d{3}\s[A-Z]{2}$'
    if not re.match(pattern, message.text.upper()):
        await message.answer(f"Xatolik iltimos qaytadan jiriting \nMisol: <b>01 A 123 AB</b> ko'rinishida")
        await state.set_state(DriverUpdateStates.car_number)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, car_number=message.text)
    await message.answer(f"✅ Mashina raqami {message.text} ga ozgartirildi !")
    await state.clear()


@driver_router.message(StateFilter(None))
async def default_handler(message: Message) -> None:
    await message.answer('Salom', reply_markup=driver_keyboard_btn().as_markup(resize_keyboard=True))
