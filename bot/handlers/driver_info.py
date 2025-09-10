import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.filters.checker import IsDriver
from bot.handlers.admin import driver_candidates
from bot.handlers.commands import myinfo_command_handler
from bot.keyboard.inline import RequestDrivingButtons
from bot.keyboard.reply import back_button_markup
from bot.states.user import DriverUpdateStates
from database import Driver, User
from utils.face_detect import has_face

driver_info_router = Router()
driver_info_router.message.filter(IsDriver())
driver_info_router.callback_query.filter(IsDriver())


@driver_info_router.callback_query(F.data.startswith("cancel"))
async def cancel_callback_query(callback: CallbackQuery) -> None:
    await callback.answer("Hazillashdingizmi 😄 kulguli, <b>Bekor qilindi</b>")
    await callback.message.delete()


@driver_info_router.callback_query(F.data.startswith(RequestDrivingButtons.CONFIRM.callback_data))
async def confirm_driving(callback: CallbackQuery, bot: Bot) -> None:
    await callback.message.edit_reply_markup()
    admins = await User.filter(User.is_admin)

    for admin in admins:
        await bot.copy_message(admin.id, callback.from_user.id, callback.message.message_id)
        await bot.send_message(admin.id, "Taxistlikga nomzodlar bor")
        await driver_candidates(callback.message)

    await callback.answer("Tekshirish uchun adminga yuborildi", show_alert=True)


# Bekor qilingan haydovchi bolish buttonni driver anketasini o'chirib yuboradi
@driver_info_router.callback_query(F.data.startswith(RequestDrivingButtons.REJECTION.callback_data))
async def delete_driver_profile_handler(callback: CallbackQuery) -> None:
    callback_data = callback.data.split()
    driver_id = int(callback_data[-1]) if len(callback_data) > 1 else callback.from_user.id
    driver = (await Driver.filter(Driver.user_id == driver_id))
    if driver:
        if driver.has_client: # Xatolik
            await callback.message.answer("Bu driverni o'chirib bolmadi")
            await callback.message.delete()
            return
        await Driver.delete(driver[0].id)

    await callback.message.edit_reply_markup()
    if len(callback_data) < 1:
        await callback.message.delete()
    else:
        await driver_candidates(callback.message)
    await callback.answer("Taxi malumotlar o'chirildi", show_alert=True)


@driver_info_router.callback_query(F.data.startswith('change_car_brand'), StateFilter(None))
async def update_car_brand_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📝 Yangi model nomini kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.car_brand)


@driver_info_router.message(DriverUpdateStates.car_brand)
async def change_car_brand_handler(message: Message, state: FSMContext):
    if not message.text.split():
        await message.answer("‼️ Mashina brendi bosh bolishi mumkun emas qaytadan kiriting")
        await state.set_state(DriverUpdateStates.car_brand)
        return
    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, car_brand=message.text)
    await message.answer(f"✅ Mashina brandi {message.text.title()}ga ozgartirildi !")
    await myinfo_command_handler(message)
    await state.clear()


@driver_info_router.callback_query(F.data.startswith('change_car_number'), StateFilter(None))
async def update_car_number_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🔢  Yangi raqamni kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.car_number)


@driver_info_router.message(DriverUpdateStates.car_number)
async def change_car_number_handler(message: Message, state: FSMContext):
    pattern = r'^(?:01|10|20|25|30|40|50|60|70|75|80|85|90|95)\s(?:[A-Z]{1}\s\d{3}\s[A-Z]{2}|\d{3}\s[A-Z]{3})$'
    if not re.match(pattern, message.text.upper()):
        await message.answer(
            "❌ Xatolik! Iltimos qaytadan kiriting.\n\n"
            "Misol: <b>01 A 123 AB</b> yoki <b>10 123 ABS</b> ko‘rinishida"
        )
        await state.set_state(DriverUpdateStates.car_number)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, car_number=message.text.upper())
    await message.answer(f"✅ Mashina raqami {message.text} ga ozgartirildi !")
    await myinfo_command_handler(message)
    await state.clear()


@driver_info_router.callback_query(F.data.startswith("change_license_term"), StateFilter(None))
async def update_taxi_license(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🧾 Litsenziyani yangilash", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.license_term)


@driver_info_router.message(DriverUpdateStates.license_term)
async def change_taxi_license(message: Message, state: FSMContext):
    if not re.match(r'^[A-Z]{2}\d{6}$', message.text):
        await message.answer("❌ Noto‘g‘ri format! Litsenziya ko'rinishi \nMasalan: KA123456")
        await state.set_state(DriverUpdateStates.license_term)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, license_term=message.text)
    await message.answer(f"✅ Litsenziya yangilandi")
    await myinfo_command_handler(message)
    await state.clear()


@driver_info_router.callback_query(F.data.startswith("change_image"), StateFilter(None))
async def update_driver_image(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🗿 Yangi rasmni kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverUpdateStates.image)


@driver_info_router.message(DriverUpdateStates.image)
async def change_driver_image(message: Message, state: FSMContext, bot: Bot):
    if (not message.photo) or not await has_face(bot, message.photo[-1].file_id):
        await message.answer("Rasm yoki odam yuzi aniqlanmadi\nIltimos o'z rasmingizni yuboring")
        await state.set_state(DriverUpdateStates.image)
        return

    driver = (await Driver.filter(Driver.user_id == message.from_user.id))[0]
    await Driver.update(driver.id, image=message.photo[-1].file_id)
    await message.answer("✅  Haydovchi rasmi yangilandi")
    await myinfo_command_handler(message)
    await state.clear()
