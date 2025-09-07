import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.filters.checker import IsDriver
from bot.keyboard.reply import DriverButtons, driver_keyboard_btn, back_button_markup
from bot.states.user import DriverUpdateStates
from database import Driver
from utils.face_detect import has_face

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


@driver_router.message(IsDriver(), F.text == DriverButtons.CHANGE_LICENSE_TERM, StateFilter(None))
async def update_taxi_license(message: Message, state: FSMContext):
    await message.answer("🧾 Litsenziyani yangilash", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.license_term)


@driver_router.message(DriverUpdateStates.license_term)
async def change_taxi_license(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(f"Xatolik litsenziya ID da str va raqam kiritiladi")
        await state.set_state(DriverUpdateStates.license_term)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, license_term=message.text)
    await message.answer(f"✅ Litsenziya yangilandi")
    await state.clear()


@driver_router.message(IsDriver(), F.text == DriverButtons.CHANGE_IMAGE, StateFilter(None))
async def update_driver_image(message: Message, state: FSMContext):
    await message.answer("🗿 Yangi rasmni kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.image)


@driver_router.message(DriverUpdateStates.image)
async def change_driver_image(message: Message, state: FSMContext, bot: Bot):
    if (not message.photo) or not await has_face(bot, message.photo[-1].file_id):
        await message.answer("Rasm yoki odam yuzi aniqlanmadi\nIltimos o'z rasmingizni yuboring")
        await state.set_state(DriverUpdateStates.image)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, image=message.photo[-1].file_id)
    await message.answer("✅  Haydovchi rasmi yangilandi")
    await state.clear()


@driver_router.message(StateFilter(None))
async def default_handler(message: Message) -> None:
    await message.answer('Salom', reply_markup=driver_keyboard_btn().as_markup(resize_keyboard=True))
