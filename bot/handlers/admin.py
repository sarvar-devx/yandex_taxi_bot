from aiogram import Router
from aiogram.types import Message

from bot.filters.checker import IsAdmin

admin_router = Router()

admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


@admin_router.message()
async def admin_handler(message: Message) -> None:
    await message.answer("Salom admin !!!")
