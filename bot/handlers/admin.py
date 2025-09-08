from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.filters.checker import IsAdmin

admin_router = Router()

admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


