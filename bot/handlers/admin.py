from aiogram import Router

from bot.states.user import ChangeNameStates, DriverStates
from utils.filters import IsAdminFilter

admin_router = Router()
#
# admin_router.message.filter(IsAdminFilter())
# admin_router.callback_query.filter(IsAdminFilter())

