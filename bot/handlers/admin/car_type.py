from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.keyboard import AdminButtons, back_button_markup
from bot.utils.states import CarTypeStates
from database.models import CarType

car_type_router = Router()


@car_type_router.message(F.text == AdminButtons.NEW_CAR_TYPE)
async def create_new_car_type(message: Message, state: FSMContext):
    await message.answer("Mashina toifasi nomini kiriting", reply_markup=back_button_markup)
    await state.set_state(CarTypeStates.name)


@car_type_router.message(CarTypeStates.name)
async def car_type_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Narxini kiriting: ")
    await state.set_state(CarTypeStates.price)


@car_type_router.message(CarTypeStates.price)
async def car_type_price(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 5000:
        await message.answer(
            "Narxini kiriting <b><i>(narx arzonlashib ketdi yoki hoto kiritdiniz faqat raqamlardan iborat bo'lsin)</i></b>: ")
        await state.set_state(CarTypeStates.price)
        return

    await state.update_data(price=int(message.text))
    data = await state.get_data()
    await message.answer(f"{data['name']}: {data['price']}\nTasdiqlaysizmi",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Ha ✅", callback_data="confirm_cartype"),
                              InlineKeyboardButton(text="Yo'q ❌", callback_data="reject_cartype")]]))


@car_type_router.callback_query(F.data.startswith("confirm_cartype"))
async def confirm_car_type(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("price") is None or data.get("name") is None:
        await callback.answer("State da hatolik malumot topilmadi", show_alert=True)
        await callback.message.edit_reply_markup()
        await state.clear()
        return

    await CarType.create(**data)
    await callback.message.edit_reply_markup()
    await callback.message.answer("Yangi Car Type muvoffaqiyatli qoshildi 🎉")
    await state.clear()


@car_type_router.callback_query(F.data.startswith("reject_cartype"))
async def reject_car_type(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Malumotlar o'chirildi")
    await callback.message.edit_reply_markup()
    await callback.message.edit_text("Car Type tasdiqlanmadi")
