from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.handlers.commands import myinfo_command_handler
from bot.keyboard.reply import UserButtons
from bot.states.user import ChangeNameStates
from db import User
from utils.services import validate_name_input

user_router = Router()


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
async def order_taxi(message: Message) -> None:
    location = ReplyKeyboardBuilder()
    location.add(KeyboardButton(text="Manzilni yuborish 📍", request_location=True))
    await message.reply("Iltimos manzilingizni yuboring 📌", reply_markup=location.as_markup())

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
