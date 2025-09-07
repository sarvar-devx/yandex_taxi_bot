from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.filters.checker import IsCustomer
from bot.keyboard.reply import UserButtons
from bot.states.user import OrderTaxiStates
from bot.utils.coordinate import get_nearest_driver
from database import OrderTaxi, User, Driver

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
async def order_map(message: Message, state: FSMContext) -> None:
    lat, lon = message.location.latitude, message.location.longitude
    await state.update_data(latitude=lat, longitude=lon)

    nearest_driver, distance = await get_nearest_driver(lat, lon)

    if nearest_driver:
        user = await User.get(id_=message.from_user.id)

        await state.update_data(
            driver_id=nearest_driver,
            user_id=user.id
        )
        driver = await Driver.get(id_=nearest_driver)
        driver_user_table = await User.get(id_=driver.user_id)
        caption = (
            f"<strong>Sizga eng yaqin haydovchi topildi ! 🚖 </strong>\n"
            f"<b>Haydovchi:</b> <i>{driver_user_table.first_name} {driver_user_table.last_name}</i>\n"
            f"<b>Mashina:</b> <i>{driver.car_brand} ({driver.car_number})</i>\n"
            f"<strong>Masofa:</strong> <tg-spoiler>{distance:.2f}</tg-spoiler> km"
        )

        await message.answer_photo(photo=f'{driver.image}', caption=caption, reply_markup=ReplyKeyboardRemove())
        # await state.set_state(OrderTaxiStates.finish)

    else:
        await message.reply("Afsuski, hozircha yaqin atrofda haydovchi topilmadi ❌")


@user_router.message(F.text == UserButtons.ORDER_HISTORY)
async def order_history(message: Message) -> None:
    user_history = await OrderTaxi.get(message.from_user.id)
    await message.answer("Hozircha mavjud emas NEW UPDATE TO NIGHT !!!")
