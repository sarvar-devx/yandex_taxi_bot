from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import bot.utils.services as services
from bot.filters import IsCustomer
from bot.keyboard import user_order_type, UserButtons, get_location, back_button_markup
from bot.keyboard.inline import driver_order_keyboard
from bot.utils.coordinate import get_nearest_driver, calculate_arrival_time
from bot.utils.states import OrderStates
from database import Order, User, Driver, CarType, Address

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
    await state.set_state(OrderStates.pickup_location)
    await message.reply("Iltimos manzilingizni yuboring 📌", reply_markup=get_location())


@user_router.message(OrderStates.pickup_location, F.location)
async def order_get_pickup_location(message: Message, state: FSMContext) -> None:
    """
    Handle user location:
    - Save latitude & longitude
    - Set state to `order_type`
    - Ask user to choose car type
    """
    await state.update_data(pickup_location=message.location)
    await state.set_state(OrderStates.drop_location)
    await message.answer(text="Manzilingiz olindi! 📌", reply_markup=back_button_markup)
    await message.answer(text="Bormoqchi bo'lgan manzilingizni yuboring 👇🏻!!!",
                         reply_markup=get_location())


@user_router.message(OrderStates.drop_location)
async def order_get_drop_location(message: Message, state: FSMContext) -> None:
    if not message.location:
        await message.answer("🤬 Kalla sanga lakatsiya yubor dedim 📍(lakatsiya yubor)")
        await state.set_state(OrderStates.drop_location)
        return

    car_types = await CarType.all()
    await state.update_data(drop_location=message.location)
    rate_price_msg = "🚖 Tariflar narxi: \n"

    for car_type in car_types:
        rate_price_msg += f"{car_type.name}: {car_type.price}\n"
    await message.answer(rate_price_msg)
    await message.answer(text="Sizga Maqul keladigan Moshina turi 👇🏻", reply_markup=user_order_type(car_types))
    await state.set_state(OrderStates.order_type)


@user_router.callback_query(OrderStates.order_type, lambda c: c.data in services.CAR_TYPE_NAMES)
async def order_type(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle car type selection:
    - Save selected type
    - Find nearest driver
    - Show driver info with photo
    """
    await state.update_data(order_type=callback.data)
    user = await User.get(id_=callback.from_user.id)
    data = await state.get_data()
    pickup_lat, pickup_lon = data['pickup_location'].latitude, data['pickup_location'].longitude

    # --- 1. Shartlarga mos haydovchilarni olish ---
    drivers = await Driver.filter(
        (Driver.is_active == True) &
        (Driver.has_client == False) &
        (Driver.car_type_id == car_type.id)
    )

    if not drivers:
        await callback.message.answer("❌ Mos keladigan haydovchi topilmadi")
        await state.clear()
        return


    # ========== YANGI QISM - BUYURTMA YARATISH ==========
    address = await Address.create(
        user_id=user.id,
        latitude=pickup_lat,
        longitude=pickup_lon
    )

    car_type = (await CarType.filter(CarType.name == callback.data))[0]
    order = await Order.create(
        user_id=user.id,
        car_type_id=car_type.id,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lon,
        drop_latitude=data['drop_location'].latitude,
        drop_longitude=data['drop_location'].longitude,
        status=Order.OrderStatus.PENDING,  # Kutilmoqda
        pickup_address_id=address.id,
        estimated_price=car_type.price,
    )
    # ================================================
    nearest_driver, distance = await get_nearest_driver(pickup_lat, pickup_lon)

    if nearest_driver:
        user = await User.get(id_=callback.from_user.id)

        await state.update_data(
            driver_id=nearest_driver,
            user_id=user.id
        )

        driver = await Driver.get(id_=nearest_driver)
        keyboard = driver_order_keyboard(order_id=order.id)

        await callback.bot.send_message(
            chat_id=driver.user_id,  # Driver telegram ID
            text=f"🆕 Yangi buyurtma!\n📍 Masofa: {distance:.2f} km",
            reply_markup=keyboard
        )

        driver_user_table = await User.get(id_=driver.user_id)
        caption = (
            f"<strong>Sizga eng yaqin haydovchi topildi ! 🚖 </strong>\n"
            f"<b>Haydovchi:</b> <i>{driver_user_table.first_name} {driver_user_table.last_name}</i>\n"
            f"<b>Mashina:</b> <i>{driver.car_brand} ({driver.car_number})</i>\n"
            f"<strong>Masofa:</strong> <tg-spoiler>{distance:.2f}</tg-spoiler> km\n"
            f"<strong>Taxminiy kelish vaqti:</strong> <tg-spoiler>{await calculate_arrival_time(distance)}</tg-spoiler>"
        )
        await callback.message.answer_photo(photo=f'{driver.image}', caption=caption)
        await callback.message.answer("⏳ Buyurtmangiz driverga yuborildi. Kutib turing...")

    else:
        await order.delete(id_=order.id)
        await callback.message.reply("Afsuski, hozircha yaqin atrofda haydovchi topilmadi ❌")
    await state.clear()


@user_router.message(F.text == UserButtons.ORDER_HISTORY)
async def order_history(message: Message) -> None:
    """
    Show user's taxi order history
    """
    user_history = await Order.get(message.from_user.id)
    await message.answer("Hozircha mavjud emas NEW UPDATE TO NIGHT !!!")
