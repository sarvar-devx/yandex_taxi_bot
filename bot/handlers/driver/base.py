from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.filters import DriverHasPermission
from bot.utils.coordinate import calculate_arrival_time
from database import Driver, DriverLocation, Order, User

driver_router = Router()
driver_router.message.filter(DriverHasPermission())
driver_router.callback_query.filter(DriverHasPermission())


@driver_router.message(F.location, StateFilter("driver_location"))
async def driver_send_location(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    driver = await Driver.get(user_id=message.from_user.id, relationships=[Driver.car_type])

    toll = float(driver.car_type.price) if driver.car_type and driver.car_type.price else 0.0

    location = await DriverLocation.get(driver_id=driver.id)
    if location:
        await location.update(latitude=lat, longitude=lon, toll=toll)
    else:
        await DriverLocation.create(driver_id=driver.id, latitude=lat, longitude=lon, toll=toll)

    await message.answer(
        "📍 Lokatsiyangiz yangilandi. Buyurtmalarni kuting 🚖",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@driver_router.callback_query(F.data.startswith("accept_order"))
async def driver_accept_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    # nearest_driver, distance = await get_nearest_driver(data['latitude'], data['longitude'])

    # Ma'lumotlarni olish
    order = await Order.get(id_=order_id)
    driver = await Driver.get(user_id=callback.from_user.id)

    # Tekshirish - buyurtma allaqachon qabul qilinganmi?
    if order.status != Order.OrderStatus.PENDING:
        await callback.answer("❌ Bu buyurtma allaqachon boshqa driver qabul qilgan!", show_alert=True)
        return

    # Buyurtmani qabul qilish
    order.status = Order.OrderStatus.ACCEPTED
    order.driver_id = driver.id  # Driver ID sini saqlash
    await order.commit()

    driver.has_client = True  # Driver bandligini belgilash
    await driver.commit()

    # User ma'lumotlarini olish
    user = await User.get(id_=order.user_id)
    driver_user = await User.get(id_=driver.user_id)

    # Masofani hisoblash (order dan lat/lon olish)
    driver_location = await DriverLocation.get(driver_id=driver.id)
    distance = 0                                            # Default qiymat
    if driver_location:
        from bot.utils.coordinate import haversine
        distance = haversine(
            order.pickup_latitude, order.pickup_longitude,
            driver_location.latitude, driver_location.longitude
        )
    # nearest_driver, distance = await get_nearest_driver(data['latitude'], data['longitude'])

    # ENDI userga driver ma'lumotlarini yuborish
    caption = f""" ✅ Sizning buyurtmangizni driver qabul qildi! 🚖

👤 Driver: {driver_user.first_name} {driver_user.last_name}
🚗 Mashina: {driver.car_brand} ({driver.car_number})
📍 Masofa: {distance:.2f} km
🕐  Kelish vaqti: {await calculate_arrival_time(distance)}

Haydovchi kelmoqda ...
    """

    # User ga driver rasmini yuborish
    try:
        await callback.bot.send_photo(
            chat_id=user.id,
            photo=driver.image,
            caption=caption,
            # add button canceled !!!
        )
    except:
        # Agar rasm yuborishda xatolik bo'lsa, faqat matn yuborish
        await callback.bot.send_message(chat_id=user.id, text=caption)

    # Driver ga javob berish va tugmalarni olib tashlash
    await callback.message.edit_text(
        text=f"✅ Buyurtmani qabul qildingiz!\n\n"
             f"👤 Mijoz: {user.first_name}\n"
             f"📍 Mijoz lokatsiyasi yuborildi",
        reply_markup=None  # Tugmalarni olib tashlash
    )

    await callback.bot.send_location(
        chat_id=driver.user_id,
        latitude=order.pickup_latitude,
        longitude=order.pickup_longitude
    )

    await callback.answer("✅ Buyurtma qabul qilindi!")


@driver_router.callback_query(F.data.startswith("reject_order"))
async def driver_reject_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])

    order = await Order.get(id_=order_id)
    driver = await Driver.get(user_id=callback.from_user.id)

    order.status = Order.OrderStatus.CANCELLED
    order.driver_id = driver.id
    await order.commit()

    # User ga xabar berish
    user = await User.get(id_=order.user_id)
    await callback.bot.send_message(
        chat_id=user.id,
        text="❌ Afsuski, sizning buyurtmangiz driver tomonidan rad etildi."
    )

    # Driver ga javob berish
    await callback.message.edit_text(
        text="❌ Buyurtmani rad etdingiz",
        reply_markup=None
    )

    await callback.answer("Buyurtma rad etildi")
