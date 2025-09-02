from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboard.reply import phone_number_rkb
from bot.states.user import UserStates
from config import conf
from db import User
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
