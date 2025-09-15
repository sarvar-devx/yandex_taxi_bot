from aiogram import Router

from bot.filters import IsAdmin
from bot.handlers.admin.base import admin_router, driver_candidates
from bot.handlers.admin.car_type import car_type_router

admin_routers = Router()
admin_routers.message.filter(IsAdmin())
admin_routers.callback_query.filter(IsAdmin())

admin_routers.include_routers(admin_router, car_type_router)
