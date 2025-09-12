import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.handlers.admin import driver_candidates
from bot.keyboard import RequestDrivingButtons, phone_number_rkb, UserButtons, back_button_markup
from bot.states.user import UserStates, DriverStates
from database import User, Driver, CarType
from utils.face_detect import has_face
from utils.services import validate_name_input, send_first_name, send_last_name, greeting_user, driver_info_msg

register_router = Router()


# Bekor qilingan haydovchi bolish buttonni driver anketasini o'chirib yuboradi
@register_router.callback_query(F.data.startswith(RequestDrivingButtons.REJECTION.callback_data))
async def delete_driver_profile_handler(callback: CallbackQuery) -> None:
    callback_data = callback.data.split()
    driver_id = int(callback_data[-1]) if len(callback_data) > 1 else callback.from_user.id
    driver = await Driver.get(user_id=driver_id)
    if driver:
        if driver.has_client:  # Xatolik
            await callback.message.answer("Bu driverni o'chirib bolmadi")
            await callback.message.delete()
            return
        await Driver.delete(driver.id)

    await callback.message.edit_reply_markup()
    if len(callback_data) < 2:
        await callback.message.delete()
    else:
        await driver_candidates(callback.message)
    await callback.answer("Taxi malumotlar o'chirildi", show_alert=True)


# first_name qabul qiladi va tekshiradi kegin last_name ga yonaltrish
@register_router.message(UserStates.first_name)
async def handle_first_name_input(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_first_name, state):
        return

    await send_last_name(message, state)
    await state.update_data(first_name=message.text.title())


# User familiyasin saqalsh va familiya button ga yonaltrish
@register_router.message(UserStates.last_name)
async def handle_last_name_input(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_last_name, state):
        return

    await state.update_data(last_name=message.text.title())
    await message.answer('📞 <b>Telefon raqamingizni yuboring.</b>', reply_markup=phone_number_rkb)
    await state.set_state(UserStates.phone_number)


# User telefon raqamini saqlash
@register_router.message(UserStates.phone_number)
async def handle_phone_input(message: Message, state: FSMContext) -> None:
    if message.contact is None or message.contact.user_id != message.from_user.id:
        await message.answer("<b>🙅 Telefon raqamni pastdagi tugma orqali yuboring 👇</b>", reply_markup=phone_number_rkb)
        return
    phone_number = message.contact.phone_number[-9:]
    user_data = await state.get_data()
    user_data.update({
        'phone_number': phone_number,
    })
    await User.update(message.from_user.id, **user_data)
    await greeting_user(message)
    await state.clear()


# Oddi user driver bolmoqchi bolsa javob beruvchi buttonlar
@register_router.message(F.text == UserButtons.BECOME_DRIVER, StateFilter(None))
async def become_to_driver(message: Message, state: FSMContext) -> None:
    if driver := await Driver.get(user_id=message.from_user.id, relationships=[Driver.car_type]):
        msg = (f'<a href="tg://user?id={driver.user_id}">{driver.user.first_name}</a> Sizning malumotlaringiz\n\n' +
               driver_info_msg(driver))
        await message.answer(
            f'\nHurmatli <a href="tg://user?id={driver.user_id}">{driver.user.first_name}</a> taxi bo\'lib ishlashni xoxlaysizmi')
        await message.answer_photo(driver.image, caption=msg, reply_markup=RequestDrivingButtons.get_markup())
        return

    if await User.filter((User.id == message.from_user.id) & (User.is_admin)):
        await message.answer("Uzur siz adminsiz sizga driver bolish mumikin emas")
        return

    await state.update_data(user_id=message.from_user.id)

    car_type = (await CarType.filter(CarType.name == "START"))[0]
    await state.update_data(car_type_id=car_type.id)
    await message.answer("Rasmingizni kiriting", reply_markup=back_button_markup)
    await state.set_state(DriverStates.image)


# Haydovchi rasmini qabul qilib avto rusumini saqlash buttoniga yonaltrish
@register_router.message(DriverStates.image)
async def handle_image_input(message: Message, state: FSMContext, bot: Bot) -> None:
    if (not message.photo) or not await has_face(bot, message.photo[-1].file_id):
        await message.answer("Rasm yoki odam yuzi aniqlanmadi\nIltimos o'z rasmingizni yuboring")
        await state.set_state(DriverStates.image)
        return

    await state.update_data(image=message.photo[-1].file_id)
    await message.answer("Mashina rusmini kiriting: ")
    await state.set_state(DriverStates.car_brand)


# Haydovchi ni mashina rusumini saqlab mashina raqamini saqalsh ga yonaltrish
@register_router.message(DriverStates.car_brand)
async def handle_car_brande_input(message: Message, state: FSMContext) -> None:
    if not re.match(r'^[a-zA-Z0-9\s-]+$', message.text):
        await message.answer("Mashina rusumi aniqlanmadi iltimos qaytadan harakat qiling")
        await state.set_state(DriverStates.car_brand)
        return

    await state.update_data(car_brand=message.text)
    await message.answer("Mashina raqamini kiriting")
    await state.set_state(DriverStates.car_number)


# Driver mashina raqamini qabul qilib litsenziyaga yonaltrish
@register_router.message(DriverStates.car_number)
async def handle_car_number_input(message: Message, state: FSMContext) -> None:
    pattern = r'^(?:01|10|20|25|30|40|50|60|70|75|80|85|90|95)\s(?:[A-Z]{1}\s\d{3}\s[A-Z]{2}|\d{3}\s[A-Z]{3})$'
    if not re.match(pattern, message.text.upper()):
        await message.answer(
            "❌ Xatolik! Iltimos qaytadan kiriting.\n\n"
            "Misol: <b>01 A 123 AB</b> yoki <b>10 123 ABS</b> ko‘rinishida"
        )
        await state.set_state(DriverStates.car_number)
        return

    await state.update_data(car_number=message.text.upper())
    await message.answer("Yandex litsenziya id raqamini kiriting:")
    await state.set_state(DriverStates.license_term)


# Litsenziyani qabul qiladi qiymat bolsa boldi True qaytarad
@register_router.message(DriverStates.license_term)
async def handle_license_input(message: Message, state: FSMContext) -> None:
    if not re.match(r'^[A-Z]{2}\d{6}$', message.text):
        await message.answer("❌ Noto‘g‘ri format! Litsenziya ko'rinishi \nMasalan: KA123456")
        await state.set_state(DriverStates.license_term)
    else:
        await state.update_data(license_term=message.text)
        driver_data = await state.get_data()
        await Driver.create(**driver_data)
        await message.answer(f"<b>Ma'lumotlar muvaffaqiyatli saqlandi</b>")
        await become_to_driver(message, state)
        await message.answer("Malumotlaringizni tugmani bosish orqali tasdiqlaing 👆")
        await state.clear()
