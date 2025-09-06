from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.checker import IsCustomer
from bot.handlers.commands import myinfo_command_handler
from bot.keyboard.reply import UserButtons
from bot.states.user import ChangeNameStates, OrderTaxiStates
from bot.utils.coordinate import get_nearest_driver
from database import User, OrderTaxi
from utils.services import validate_name_input

user_router = Router()
user_router.message.filter(IsCustomer())
user_router.callback_query(IsCustomer())


@user_router.message(F.text == UserButtons.CHANGE_FIRST_NAME, StateFilter(None))
async def send_first_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Ismingizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.first_name)


@user_router.message(ChangeNameStates.first_name)
async def change_first_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_first_name_handler, state):
        return

    await User.update(message.from_user.id, first_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning ismingiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()


# @user_router.message(F.text == UserButtons.GET_CHAT_ID)
# async def get_my_id(message: Message):
#     await message.answer(f"Chat_id: <code>{message.chat.id}</code>")


@user_router.message(F.text == UserButtons.CHANGE_LAST_NAME, StateFilter(None))
async def send_last_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer("✍️ <b>Familiyangizni kiriting</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChangeNameStates.last_name)


@user_router.message(ChangeNameStates.last_name)
async def change_last_name_handler(message: Message, state: FSMContext) -> None:
    if not await validate_name_input(message, send_last_name_handler, state):
        return

    await User.update(message.from_user.id, last_name=message.text.title())
    await message.answer(
        f"Hurmatli <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> sizning familiyangiz {message.text.title()} ga uzgartirildi!")
    await myinfo_command_handler(message)
    await state.clear()


@user_router.message(F.text == UserButtons.ORDER_TAXI)
async def order_taxi(message: Message, state: FSMContext) -> None:
    location = ReplyKeyboardBuilder()
    location.add(KeyboardButton(text="Manzilni yuborish 📍", request_location=True))
    await state.set_state(OrderTaxiStates.map)

    await message.reply("Iltimos manzilingizni yuboring 📌", reply_markup=location.as_markup(resize_keyboard=True))


@user_router.message(OrderTaxiStates.map, F.location)
async def order_map(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lat, lon = message.location.latitude, message.location.longitude
    await state.update_data(latitude=lat, longitude=lon)

    nearest_driver, distance = await get_nearest_driver(session, lat, lon)

    if nearest_driver:
        await state.update_data(driver_id=nearest_driver.id, user_id=message.from_user.id)
        await message.reply(
            f"Sizga eng yaqin haydovchi topildi 🚖\n"
            f"Driver: {nearest_driver.name}\n"
            f"Masofa: {distance:.2f} km"
        )
        # keyingi bosqichga o'tkazish
        # await state.set_state(OrderTaxiStates.finish)
    else:
        await message.reply("Afsuski, hozircha yaqin atrofda haydovchi topilmadi ❌")


@user_router.message(F.text == UserButtons.ORDER_HISTORY)
async def order_history(message: Message) -> None:
    user_history = await OrderTaxi.get(message.from_user.id)
    await message.answer("Hozircha mavjud emas NEW UPDATE TO NIGHT !!!")

# @user_router.message(F.text == UserButtons.BECOME_DRIVER)
# async def become_driver_handler(message: Message):
#
#     # Admin chat_id sini olish kere
#
#     await message.bot.send_message(
#         chat_id=ADMIN_CHAT_ID,
#         text=f"Foydalanuvchi {message.from_user.full_name} haydovchi bo‘lishni so‘ramoqda.",
#         reply_markup=DriverRequestButtons.get_markup(message.from_user.id)
#     )
#
#     await message.answer("✅ So‘rovingiz yuborildi, admin tasdiqlashini kuting.")
