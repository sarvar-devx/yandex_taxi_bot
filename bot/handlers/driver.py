from pyexpat.errors import messages

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.keyboard.inline import driver_order_keyboard
from bot.filters import DriverHasPermission
from bot.keyboard import get_location
from database import Driver, DriverLocation, Order, User, CarType

driver_router = Router()
driver_router.message.filter(DriverHasPermission())
driver_router.callback_query.filter(DriverHasPermission())


@driver_router.message(StateFilter(None))
async def driver_start(message: Message, state: FSMContext):
    await message.answer(
        "Assalomu alaykum, haydovchi!\nIltimos, lokatsiyangizni yuboring 📍",
        reply_markup=get_location()
    )
    await state.set_state("driver_location")


@driver_router.message(F.location, StateFilter("driver_location"))
async def driver_send_location(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    driver = await Driver.get(user_id=message.from_user.id)

    if driver.car_type_id:
        car_type = await CarType.get(driver.car_type_id)
        toll = car_type.price
    else:
        toll = 5000

    await DriverLocation.create(
        driver_id=driver.id,
        latitude=lat,
        longitude=lon,
        toll=toll
    )
    await message.answer("📍 Lokatsiyangiz saqlandi. Buyurtmalarni kuting 🚖", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@driver_router.callback_query(F.data.startswith("accept_order"))
async def driver_accept_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])

    order = await Order.get(id_=order_id)
    order.status = Order.OrderStatus.ACCEPTED
    await order.save()

    user = await User.get(id_=order.user_id)

    # Userga xabar berish
    await callback.bot.send_message(
        chat_id=user.id,
        text="✅ Sizning buyurtmangizni haydovchi qabul qildi! 🚖"
    )

    await callback.message.answer("✅ Buyurtmani qabul qildingiz")


@driver_router.callback_query(F.data.startswith("reject_order"))
async def driver_reject_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])

    order = await Order.get(id_=order_id)
    order.status = Order.OrderStatus.CANCELLED
    await order.save()

    # Userni olish
    user = await User.get(id_=order.user_id)

    # Userga xabar berish
    await callback.bot.send_message(
        chat_id=user.id,
        text="❌ Afsuski, sizning buyurtmangiz haydovchi tomonidan rad etildi."
    )
    await callback.message.answer("❌ BUyurtmani rad etdinggiz ?!")
