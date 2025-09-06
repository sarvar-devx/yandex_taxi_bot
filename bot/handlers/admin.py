from aiogram import Router
from aiogram.types import Message

from utils.filters import IsAdminFilter

admin_router = Router()

admin_router.message.filter(IsAdminFilter())
admin_router.callback_query.filter(IsAdminFilter())


@admin_router.message()
async def admin(message: Message):
    await message.answer('Adminsan')
