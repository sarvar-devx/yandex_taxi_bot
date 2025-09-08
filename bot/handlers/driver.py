from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.filters.checker import DriverHasPermission
from bot.keyboard.reply import get_location
from database import Driver, DriverLocation

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
    await DriverLocation.create(
        driver_id=driver.id,
        latitude=lat,
        longitude=lon
    )

    await message.answer("📍 Lokatsiyangiz saqlandi. Buyurtmalarni kuting 🚖", reply_markup=ReplyKeyboardRemove())
    await state.clear()
