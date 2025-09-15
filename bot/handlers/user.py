from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import bot.utils.services as services
from bot.filters import IsCustomer
from bot.keyboard import user_order_type, UserButtons, get_location, main_keyboard_btn
from bot.keyboard.reply import order_cancelled
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
    await state.update_data(latitude=lat, longitude=lon)
    await state.set_state(OrderStates.address)
    await message.answer(text="Manzilingiz olindi! 📌", reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Bormoqchi bo'lgan manzilingizni To'liq kiriting va yuboring 👇🏻!!!", )

    # await message.answer(text="🔙 Orqaga", reply_markup=back_button_markup)


@user_router.message(OrderStates.address)
async def order_address(message: Message, state: FSMContext) -> None:
    car_types = await CarType.all()
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.order_type)
    await message.answer(text="Sizga Maqul keladigan Moshina turi 👇🏻", reply_markup=user_order_type(car_types))


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
    # ========== YANGI QISM - BUYURTMA YARATISH ==========
    address = await Address.create(
        user_id=user.id,
        latitude=data['latitude'],
        longitude=data['longitude'],
        full_address=data['address'],
    )

    car_type = (await CarType.filter(CarType.name == callback.data))[0]
    order = await Order.create(
        user_id=user.id,
        car_type_id=car_type.id,
        pickup_latitude=data['latitude'],
        pickup_longitude=data['longitude'],
        status=Order.OrderStatus.PENDING,  # Kutilmoqda
        pickup_address_id=address.id,
        estimated_price=car_type.price,

    )
    # ================================================
    nearest_driver, distance = await get_nearest_driver(data['latitude'], data['longitude'])

    if nearest_driver:
        user = await User.get(id_=callback.from_user.id)

        await state.update_data(
            driver_id=nearest_driver,
            user_id=user.id
        )

        driver = await Driver.get(id_=nearest_driver)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_order:{order.id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_order:{order.id}")
            ]
        ])

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
        await callback.message.answer("⏳ Buyurtmangiz driverga yuborildi. Kutib turing...",
                                      reply_markup=order_cancelled(callback.message.from_user.id))

    else:
        await order.delete(id_=order.id)
        await callback.message.reply("Afsuski, hozircha yaqin atrofda haydovchi topilmadi ❌")
    await state.clear()


@user_router.message(F.text.startswith(UserButtons.ORDER_CANCEL))
async def order_cancel(message: Message) -> None:
    await message.reply(
        text="Buyurtma bekor qilindi ✅ Buyurtmani bekor qilish bundan keyingi buyurtma qilishga ta'sir qilishi mumkin e'tiborliroq bo'lishingizni so'raymiz !!!",
        reply_markup=main_keyboard_btn().as_markup(resize_keyboard=True))


@user_router.message(F.text == UserButtons.ORDER_HISTORY)
async def order_history(message: Message) -> None:
    """
    Show user's taxi order history
    """
    user_order_history = await Order.filter(User.id == message.from_user.id)

    if not user_order_history:
        await message.answer("📭 Sizda hali buyurtmalar tarixi mavjud emas.")
        return

    for order in user_order_history:
        driver = await Driver.get(id_=order.driver_id)
        user_driver = await User.get(id_=driver.user_id) if driver else None
        if user_driver:
            text = (
                f"📌 <b>Buyurtma #{order.id}</b>\n\n"
                f"👤 <b>Buyurtmachi:</b> {order.user.first_name} {order.user.last_name}\n"
                f"🚖 <b>Haydovchi:</b> "
                f"{user_driver.first_name} {user_driver.last_name if user_driver else 'Noma’lum'}\n"
                f"📅 <b>Kuni:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📊 <b>Status:</b> {str(order.status.value).capitalize()}\n"
            )

            await message.answer(text=text, parse_mode="HTML")
