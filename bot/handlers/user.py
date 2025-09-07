from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.checker import IsCustomer
from bot.keyboard.reply import UserButtons
from bot.states.user import OrderTaxiStates
from bot.utils.coordinate import get_nearest_driver
from database import OrderTaxi

user_router = Router()
user_router.message.filter(IsCustomer())
user_router.callback_query.filter(IsCustomer())


# @user_router.message(F.text == UserButtons.GET_CHAT_ID)
# async def get_my_id(message: Message):
#     await message.answer(f"Chat_id: <code>{message.chat.id}</code>")


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
