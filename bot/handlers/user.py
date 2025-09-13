from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

import bot.utils.services as services
from bot.filters import IsCustomer
from bot.keyboard import user_order_type, UserButtons, get_location
from bot.utils.states import OrderStates
from bot.utils.coordinate import get_nearest_driver, calculate_arrival_time
from database import Order, User, Driver, CarType

user_router = Router()
user_router.message.filter(IsCustomer())
user_router.callback_query.filter(IsCustomer())


@user_router.message(F.text == UserButtons.ORDER_TAXI)
async def order_taxi(message: Message, state: FSMContext) -> None:
    """
    Start taxi order process:
    - Set state to `location`
    - Ask user to send location
    """
    await state.set_state(OrderStates.location)
    await message.reply("Iltimos manzilingizni yuboring 📌", reply_markup=get_location())


@user_router.message(OrderStates.location, F.location)
async def order_location(message: Message, state: FSMContext) -> None:
    """
    Handle user location:
    - Save latitude & longitude
    - Set state to `order_type`
    - Ask user to choose car type
    """
    lat, lon = message.location.latitude, message.location.longitude
    car_types = await CarType.all()
    await state.update_data(latitude=lat, longitude=lon)
    await state.set_state(OrderStates.order_type)
    await message.answer(text="Manzilingiz olindi! 📌", reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Sizga Maqul keladigan Moshina turi 👇🏻", reply_markup=user_order_type(car_types))
    # await message.answer(text="🔙 Orqaga", reply_markup=back_button_markup)


@user_router.callback_query(OrderStates.order_type, lambda c: c.data in services.CAR_TYPE_NAMES)
async def order_type(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle car type selection:
    - Save selected type
    - Find nearest driver
    - Show driver info with photo
    """
    await state.update_data(order_type=callback.data)
    data = await state.get_data()
    nearest_driver, distance = await get_nearest_driver(data['latitude'], data['longitude'])

    if nearest_driver:
        user = await User.get(id_=callback.from_user.id)

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
            f"<strong>Masofa:</strong> <tg-spoiler>{distance:.2f}</tg-spoiler> km\n"
            f"<strong>Taxminiy kelish vaqti:</strong> <tg-spoiler>{await calculate_arrival_time(distance)}</tg-spoiler>"
        )
        await callback.message.answer_photo(photo=f'{driver.image}', caption=caption)

    else:
        await callback.message.reply("Afsuski, hozircha yaqin atrofda haydovchi topilmadi ❌")


@user_router.message(F.text == UserButtons.ORDER_HISTORY)
async def order_history(message: Message) -> None:
    """
    Show user's taxi order history
    """
    user_history = await Order.get(message.from_user.id)
    await message.answer("Hozircha mavjud emas NEW UPDATE TO NIGHT !!!")
