from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton, \
    InputMediaPhoto

from bot.filters.checker import IsAdmin
from bot.keyboard.inline import drivers_list, inline_car_types_buttons
from bot.keyboard.reply import AdminButtons
from database import Driver
from utils.services import driver_info_msg

admin_router = Router()

admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


@admin_router.message(F.text == AdminButtons.DRIVER_CANDIDATES)
async def driver_candidates(message: Message):
    drivers = await Driver.filter(Driver.has_permission == False, relationship=Driver.user)
    if len(drivers) == 0:
        await message.answer("Hozircha nomzodlar yoq")
        return
    await message.answer("Bu yerda taxistlikka nomzodlar: ", reply_markup=drivers_list(drivers))


@admin_router.callback_query(F.data.startswith("driving_candidates"))
async def callback_driving_candidates(callback: CallbackQuery):
    await driver_candidates(callback.message)


@admin_router.callback_query(F.data.startswith("driver_id"))
async def driver_request(callback: CallbackQuery):
    driver_id = int(callback.data.split()[-1])
    driver = await Driver.get(user_id=driver_id, relationship=Driver.user)
    msg = driver_info_msg(driver)

    await callback.message.edit_media(
        media=InputMediaPhoto(media=driver.image,
                              caption=msg + "\n\n------------<b> avtomobil turini tanlang </b>------------"),
        reply_markup=inline_car_types_buttons(driver_id))
    await callback.message.answer("Tasdiqlamasingiz: ", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Bu driver malumotlarini tasiqlamayman",
                                               callback_data=f"reject_driving: {driver_id}")]]))


@admin_router.callback_query(F.data.startswith("driver_car_type"))
async def give_car_type(callback: CallbackQuery):
    callback_data = callback.data.split()
    driver_id = int(callback_data[-1])
    driver = await Driver.get(user_id=driver_id, relationship=Driver.user)
    await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
    if not driver or driver.has_permission:
        await callback.answer("Bu driverda permission bor yoki driver aniqlanmadi", show_alert=True)
        return

    car_type = getattr(Driver.CarType, callback_data[1], Driver.CarType.START)

    await Driver.update(user_id=driver_id, car_type=car_type)
    msg = driver_info_msg(driver)
    await callback.message.edit_media(
        media=InputMediaPhoto(media=driver.image,
                              caption=msg + "\n\n------------<b>Userga taxistlik xuquqi berasizmi</b>------------"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Ha beraman 🚖",
                                      callback_data=f"permission_to_driver: {driver_id}")],
                [InlineKeyboardButton(text="❌ Bu driver malumotlarini tasiqlamayman",
                                      callback_data=f"reject_driving: {driver_id}")],
                [InlineKeyboardButton(text="Taxistlikka nomzodlar", callback_data="driving_candidates")]]))


@admin_router.callback_query(F.data.startswith("permission_to_driver"))
async def give_permission_to_driver(callback: CallbackQuery, bot: Bot):
    driver_id = int(callback.data.split()[-1])
    driver = await Driver.get(user_id=driver_id)
    if not driver or driver.has_permission:
        await callback.answer("Bu driverda permission bor yoki driver aniqlanmadi", show_alert=True)
        return

    await Driver.update(user_id=driver_id, has_permission=True)
    await callback.answer("Permission berildi 🎉", show_alert=True)
    await callback.message.edit_reply_markup("", InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Permission berildi 🎉",
                                               copy_text=CopyTextButton(text="Permission berildi 🎉"))]]))
    await bot.send_message(driver_id,
                           text="🎉 Tabriklaymiz sizga taxsistlik xuquqi berildi\nEndi bemalol taxistlik qilishingiz mumkin /start")