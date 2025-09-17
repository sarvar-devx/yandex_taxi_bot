import time

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.filters import DriverHasPermission
from bot.keyboard import the_driver_has_arrived_keyboard
from bot.utils.coordinate import calculate_arrival_time, haversine
from database import Driver, DriverLocation, Order, User, CarType

driver_router = Router()
driver_router.message.filter(DriverHasPermission())
driver_router.callback_query.filter(DriverHasPermission())

driver_waiting_times = {}  # {order_id: start_time}


# Vaxtni xisoblash funksiyasi
def calculate_extra_fee(order_id: int):
    start_time = driver_waiting_times.get(order_id)
    if not start_time:
        return 0, 0

    wait_minutes = (time.time() - start_time) / 60
    extra_minutes = max(0, wait_minutes - 5)
    extra_fee = int(extra_minutes) * 1000
    return int(wait_minutes), extra_fee


# Mijozni kutish
@driver_router.callback_query(F.data.startswith("driver_arrived"))
async def driver_arrived_button(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    order = await Order.get(order_id)
    user_id = order.user_id

    # Kutish uchun start time
    driver_waiting_times[order_id] = time.time()

    await bot.send_message(
        chat_id=user_id,
        text="🚖 Sizning haydovchingiz yetib keldi! "
             "\nHaydovchi sizni 5 daqiqa tekin kutadi keyin"
             "\ndaqiqasiga 1000 so'mdan echadi"
    )
    # wit_minutes, extra_fee = calculate_extra_fee(order_id)

    await callback.message.edit_text(
        "Mijozga xabar yuborildi",
        reply_markup=the_driver_has_arrived_keyboard(order_id, step="arrived")
    )


# Harakatni boshlash
@driver_router.callback_query(F.data.startswith("we_left"))
async def driver_we_left_button(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    wit_minutes, extra_fee = calculate_extra_fee(order_id)

    await callback.message.edit_text(
        f"🚖 Yo‘lga chiqildi!\n⌛ Kutish vaqti: {wit_minutes:.1f} daqiqa\n"
        f"💰 Qo‘shimcha to‘lov: {extra_fee} so‘m",
        reply_markup=the_driver_has_arrived_keyboard(order_id, step="left")
    )
    # await callback.message.edit_text("Yolga chiqildi")


# Yetib keish vaxtini xisoblash
@driver_router.callback_query(F.data.startswith("we_arrived"))
async def driver_we_arrived_button(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    order = await Order.get(order_id)
    user_id = order.user_id

    # === Asosiy km narxi ===
    distance = haversine(
        order.pickup_latitude, order.pickup_longitude,
        order.drop_latitude, order.drop_longitude
    )
    car_type = await CarType.get(order.car_type_id)
    base_price = distance * car_type.price

    wait_minutes, extra_fee = calculate_extra_fee(order_id)

    # === Yakuniy summa ===
    total_price = int(base_price) + extra_fee

    # Buyurtma yakunlanadi
    order.status = Order.OrderStatus.COMPLETED
    await order.commit()

    user = await User.get(order.user_id)
    await callback.bot.send_message(
        chat_id=user.id,
        text=(
            f"✅ Siz manzilingizga yetib keldingiz!\n\n"
            f"📍 Masofa: {distance:.2f} km\n"
            f"💰 Asosiy narx: {int(base_price):,} so'm\n"
            f"⏱ Kutish vaqti: {wait_minutes:.1f} daqiqa\n"
            f"➕ Qo'shimcha: {extra_fee:,} so'm\n\n"
            f"💵 Jami to'lov: <b>{total_price:,} so'm</b>"
        )
    )

    await callback.message.answer(
        f"✅ Buyurtma yakunlandi!\n"
        f"Kutish: {wait_minutes:.1f} daqiqa\n"
        f"Qo‘shimcha to‘lov: {extra_fee} so‘m"
    )

    # === Haydovchiga ham xabar beramiz ===
    await callback.message.edit_text(
        f"Mijoz manzilda ✅\nUmumiy summa: {total_price:,} so'm"
    )

    # Kutish vaqtini tozalash
    driver_waiting_times.pop(order_id, None)


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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
    distance = 0  # Default qiymat
    if driver_location:
        from bot.utils.coordinate import haversine
        distance = haversine(
            order.pickup_latitude, order.pickup_longitude,
            driver_location.latitude, driver_location.longitude
        )

    # ENDI userga driver ma'lumotlarini yuborish
    caption = f""" ✅ Sizning buyurtmangizni driver qabul qildi! 🚖

👤 Driver: {driver_user.first_name} {driver_user.last_name}
🚗 Mashina: {driver.car_brand} ({driver.car_number})
📍 Masofa: {distance:.2f} km
📱 Aloqa: {driver_user.phone_number}
🕐  Haydovchi: {await calculate_arrival_time(distance)} daqiqada keladi

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
    await callback.message.answer(
        text=f"✅ Buyurtmani qabul qildingiz!\n\n"
             f"👤 Mijoz: {user.first_name}\n"
             f"📍 Mijoz lokatsiyasi yuborildi",
        reply_markup=the_driver_has_arrived_keyboard(order_id, step="start")  # Tugmalarni olib tashlash
    )

    await callback.bot.send_location(
        chat_id=driver.user_id,
        latitude=order.pickup_latitude,
        longitude=order.pickup_longitude
    )

    await callback.answer("✅ Buyurtma qabul qilindi!")
    await callback.message.delete()


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
    await callback.message.delete()
