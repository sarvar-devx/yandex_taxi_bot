import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from bot.keyboard.reply import phone_number_rkb, UserButtons
from bot.states.user import UserStates, DriverStates
from config import conf
from db import User
from utils.face_detect import has_face
from utils.services import validate_name_input, send_first_name, send_last_name, greeting_user

register_router = Router()


# first_name qabul qiladi va tekshiradi kegin last_name ga otkazadi
@register_router.message(UserStates.first_name)
async def handle_first_name_input(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_first_name, state):
        return

    await send_last_name(message, state)
    await state.update_data(first_name=message.text.title())


@register_router.message(UserStates.last_name)
async def handle_last_name_input(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_last_name, state):
        return

    await state.update_data(last_name=message.text.title())
    await message.answer('📞 <b>Telefon raqamingizni yuboring.</b>', reply_markup=phone_number_rkb)
    await state.set_state(UserStates.phone_number)


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
    # if message.from_user.id in conf.bot.get_admin_list:
    #     await back_admin_menu_handler(message, state)
    #     return
    await greeting_user(message)
    await state.clear()


@register_router.message(F.text == UserButtons.BECOME_DRIVER, StateFilter(None))
async def become_to_driver(message: Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.from_user.id)
    await message.answer("Rasmingizni kiriting",
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=UserButtons.BACK)]],
                                                          resize_keyboard=True))
    await state.set_state(DriverStates.image)


@register_router.message(DriverStates.image)
async def handle_image_input(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.photo:
        await message.answer("Iltimos, faqat rasm yuboring.")
        return

    if not await has_face(bot, message.photo[-1].file_id):
        await message.answer("bu rasmda odam yuzi aniqlanmadi\nIltimos o'z rasmingizni yuboring")
        await state.set_state(DriverStates.image)
        return

    await state.update_data(image=message.photo[-1].file_id)
    await message.answer("Moshina rusmini kiriting: ")
    await state.set_state(DriverStates.car_brand)


@register_router.message(DriverStates.car_brand)
async def handle_car_brande_input(message: Message, state: FSMContext) -> None:
    if not re.match(r'^[a-zA-Z0-9\s-]+$', message.text):
        await message.answer("Mashina rusumi aniqlanmadi iltimos qaytadan harakat qiling")
        await state.set_state(DriverStates.car_brand)
        return

    await state.update_data(car_brand=message.text)
    await message.answer("Mashina raqamini kiriting")
    await state.set_state(DriverStates.car_number)


@register_router.message(DriverStates.car_number)
async def handle_car_number_input(message: Message, state: FSMContext) -> None:
    if not re.match(r'^\d{2}\s[A-Z]{1}\s\d{3}\s[A-Z]{2}$', message.text):
        await message.answer(f"Xatolik iltimos qaytadan jiriting \nMisol: [ A 968 EG ] ko'rinishida")
        await state.set_state(DriverStates.car_number)
        return

    await state.update_data(car_number=message.text)
    await message.answer("Yandex litsenziya id raqamini kiriting:")
    await state.set_state(DriverStates.license_term)


@register_router.message(DriverStates.license_term)
async def handle_license_input(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(f"Xatolik litsenziya IDda str va raqam kiritiladi")
        await state.set_state(DriverStates.license_term)
        return

    await state.update_data(license_term=message.text)
    await message.answer("Profil muvaffaqiyatli yangilandi !")
