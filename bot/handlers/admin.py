from aiogram import Router, F
from aiogram.types import Message

from bot.filters.checker import IsAdmin
from bot.keyboard.inline import drivers_list
from bot.keyboard.reply import AdminButtons
from database import Driver

admin_router = Router()

admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


@admin_router.message(F.text == AdminButtons.DRIVER_INQUIRIES)
async def admin_driver_inquiries(message: Message):
    drivers = await Driver.filter(Driver.has_permission == False, relationship=Driver.user)
    await message.answer("Bu yerda texistlikka nomzidlar: ", reply_markup=drivers_list(drivers))
