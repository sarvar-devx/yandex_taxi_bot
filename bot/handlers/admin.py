from aiogram import Router
from aiogram.types import Message

from bot.filters.checker import IsAdmin

admin_router = Router()


#
# admin_router.message.filter(IsAdminFilter())
# admin_router.callback_query.filter(IsAdminFilter())

@admin_router.message(IsAdmin())
async def admin_handler(message: Message) -> None:
    await message.answer("Salom admin !!!")
